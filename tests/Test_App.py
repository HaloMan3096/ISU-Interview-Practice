"""
Tests for the Interview Practice Coach (app.py).

Standard library only. Run from the project folder:
    python -m unittest discover -s tests -v        (Windows: python -m unittest discover -s tests -v)

No real AI is ever called: call_llm is replaced with a fake that records the prompt it was given,
so these tests also prove what WOULD be sent to the provider.
"""
import io
import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
import zipfile
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import app  # noqa: E402

RESUME = (
    "Logan Parkhurst\n"
    "123 Main Street, Apt 4B, Springfield IL 62701\n"
    "(555) 555-0142 | logan.parkhurst@example.com | linkedin.com/in/example-user | https://github.com/example-user\n"
    "Objective: IT support intern. Born March 3, 2003.\n"
    "EXPERIENCE\n"
    "Help Desk Aide - fixed printers, reset passwords with Python scripts.\n"
)
# Everything in RESUME that must never reach the AI (all of it is made-up sample data).
PII = ["Logan", "LOGAN", "Parkhurst", "PARKHURST", "Main Street", "Springfield", "62701", "555-0142",
       "example.com", "example-user", "March 3"]


class RedactTestCase(unittest.TestCase):
    """Base class: every test starts with no remembered names and redaction switched on."""

    def setUp(self):
        app._known_terms.clear()
        p1 = mock.patch.object(app, "REDACT", True)
        p2 = mock.patch.object(app, "EXTRA_TERMS", [])
        p1.start(); p2.start()
        self.addCleanup(p1.stop); self.addCleanup(p2.stop)
        self.addCleanup(app._known_terms.clear)

    def assertRedacts(self, text, label):
        out = app.redact(text)
        self.assertIn(f"[{label}]", out, f"{text!r} -> {out!r}")
        return out

    def assertUntouched(self, text):
        self.assertEqual(app.redact(text), text)


# REDACTION RULES: each test gives the redactor text containing one kind of personal info and
# checks it becomes a placeholder.
class TestPatterns(RedactTestCase):
    # Plain, +tag and multi-part addresses (e.g. student@university.example.edu) all become
    # [EMAIL].
    def test_emails(self):
        for t in ["jo@example.com", "first.last+tag@sub.example.co.uk", "student@university.example.edu"]:
            with self.subTest(t):
                self.assertEqual(app.redact(f"Mail {t} now"), "Mail [EMAIL] now")

    # Six phone styles - (555) 555-0142, dashes, dots, spaces, +1 and no punctuation - all become
    # [PHONE].
    def test_phone_formats(self):
        for t in ["(812) 555-0142", "812-555-0142", "812.555.0142", "812 555 0142", "+1 812 555 0142", "8125550142"]:
            with self.subTest(t):
                self.assertEqual(app.redact(f"Call {t}."), "Call [PHONE].")

    # https://, http://, www. and bare linkedin.com/... or github.com/... links all become [LINK].
    def test_links(self):
        for t in ["https://github.com/someone", "http://example.com/me", "www.example.com/me",
                  "linkedin.com/in/someone", "github.com/someone"]:
            with self.subTest(t):
                self.assertRedacts(f"See {t}", "LINK")

    # A 123-45-6789 style number becomes [ID NUMBER].
    def test_ssn_style_numbers(self):
        self.assertEqual(app.redact("SSN 123-45-6789 here"), "SSN [ID NUMBER] here")

    # Street, Avenue, Ct, Blvd and 'Apt 4B' forms, plus P.O. Box, become [ADDRESS].
    def test_street_addresses(self):
        for t in ["456 Oak Street", "123 Maple Street", "42 Oak Avenue, Apt 4B", "9 Elm Ct", "500 N Main Blvd"]:
            with self.subTest(t):
                self.assertRedacts(t, "ADDRESS")
        self.assertRedacts("P.O. Box 77", "ADDRESS")
        self.assertRedacts("PO Box 123", "ADDRESS")

    # 'City, ST' forms such as Naperville, IL, St. Louis, MO and O'Fallon, IL become [LOCATION].
    def test_city_and_state(self):
        for t in ["Naperville, IL", "Peoria, IL", "St. Louis, MO", "O'Fallon, IL", "Chicago, IL   Sep. 2022"]:
            with self.subTest(t):
                self.assertRedacts(t, "LOCATION")

    # Regression: a city before the state and ZIP was leaking when there was no comma
    # ("Springfield IL 62701"). Also covers ZIP+4 and an ALL CAPS city.
    def test_city_state_zip_with_or_without_comma(self):
        self.assertEqual(app.redact("Springfield IL 62701"), "[LOCATION]")
        self.assertEqual(app.redact("Springfield, IL 62701"), "[LOCATION]")
        self.assertEqual(app.redact("Indianapolis, IN 46204-1234"), "[LOCATION]")
        self.assertEqual(app.redact("NEW YORK NY 10001"), "[LOCATION]")

    # A full address line (street, then city, state and ZIP) becomes "[ADDRESS], [LOCATION]".
    def test_home_address_line_from_a_real_layout(self):
        self.assertEqual(app.redact("456 Oak Street, Springfield IL 62704"), "[ADDRESS], [LOCATION]")

    # "Born March 3, 2003" and "DOB: 03/03/2003" become [DATE OF BIRTH].
    def test_date_of_birth(self):
        self.assertRedacts("Born March 3, 2003.", "DATE OF BIRTH")
        self.assertRedacts("DOB: 03/03/2003", "DATE OF BIRTH")

    # Empty or missing text returns an empty string and does not crash.
    def test_empty_and_none_input(self):
        self.assertEqual(app.redact(""), "")
        self.assertEqual(app.redact(None), "")


# THINGS THAT MUST NOT BE REDACTED: guards against over-redaction of normal technical text. Each
# case here has broken before or could.
class TestFalsePositives(RedactTestCase):
    """Normal technical text must survive. These are the cases that have broken before."""

    # Regression: "like AND, OR, NOT" was being read as a city plus the state code OR and turned
    # into [LOCATION].
    def test_logic_words_are_not_states(self):
        self.assertUntouched("true/false conditions, like AND, OR, NOT and “if this, then that.”")

    # "Use Python, OR the standard library" is ordinary prose, not a place, so it stays as
    # written.
    def test_state_code_followed_by_a_lowercase_word(self):
        self.assertUntouched("Use Python, OR the standard library")

    # The Languages, IDEs and Tools lines from a typical résumé come through unchanged.
    def test_skills_and_tools_lists(self):
        for t in ["Programming Languages: Python, C#, HTML/CSS, JavaScript, Ruby, Elm, C++, C, SQL, php",
                  "IDEs: Visual Studio, VS Code, RubyMine, PyCharm, Rider",
                  "Tools: Figma, Word, Power Point, Excel"]:
            with self.subTest(t):
                self.assertUntouched(t)

    # "100+ tests", "Python 3.11.4", "2019-2023" and "2-3 pages" must not look like phone numbers,
    # ZIPs or addresses.
    def test_numbers_that_are_not_phones_or_zips(self):
        for t in ["Wrote 100+ automated UI tests", "Aug. 2022 - May 2025", "Python 3.11.4", "Scored 95% in 2019-2023",
                  "Reworked 2-3 administrative pages"]:
            with self.subTest(t):
                self.assertUntouched(t)

    # Game-programming answers such as damage = f(attack, defense, armor) and onGround AND NOT
    # stunned stay intact.
    def test_damage_formula_and_jump_condition(self):
        self.assertUntouched("damage = f(attack, defense, armor); canJump = onGround AND NOT stunned")


# NAME LEARNING: the app guesses the candidate's name from the top of the résumé, remembers it in
# memory only, and removes it from later text (such as typed answers).
class TestNameLearning(RedactTestCase):
    # Nothing is removed before a résumé has been seen; afterwards the first name, last name and
    # ALL CAPS forms all become [NAME].
    def test_learns_name_from_first_line_and_removes_every_part(self):
        out = app.redact("Hi, I'm Logan Parkhurst. Parkhurst here, call me Logan.", learn=False)
        self.assertEqual(out, "Hi, I'm Logan Parkhurst. Parkhurst here, call me Logan.")  # nothing learned yet
        app.redact(RESUME, learn=True)
        out = app.redact("Hi, I'm Logan Parkhurst. Parkhurst here, call me LOGAN.")
        self.assertEqual(out, "Hi, I'm [NAME]. [NAME] here, call me [NAME].")

    # A top line written as LOGAN PARKHURST is learned, and matching is case-insensitive.
    def test_all_caps_name_line_is_recognised(self):
        app.redact("LOGAN PARKHURST\nIT support intern", learn=True)
        self.assertEqual(app.redact("logan parkhurst wrote this"), "[NAME] wrote this")

    # A line like "Name: Logan Parkhurst" is learned, even when it is not the first line.
    def test_name_label_is_recognised(self):
        app.redact("Resume\nName: Logan Parkhurst\nSkills: Python", learn=True)
        self.assertEqual(app.redact("Logan and Parkhurst"), "[NAME] and [NAME]")

    # "Parkhursting" is left alone while "Parkhurst" is replaced.
    def test_matches_whole_words_only(self):
        app.redact("Logan Parkhurst\nIT intern", learn=True)
        self.assertEqual(app.redact("Parkhursting and Parkhurst"), "Parkhursting and [NAME]")

    # A first line such as "Work Experience" must not be learned as a name.
    def test_section_headings_are_not_names(self):
        app.redact("Work Experience\nBuilt a web page", learn=True)
        self.assertEqual(app._known_terms, set())

    # A one-word first line such as "Resume" must not be learned as a name.
    def test_one_word_first_line_is_not_a_name(self):
        app.redact("Resume\nSkills: Python", learn=True)
        self.assertEqual(app._known_terms, set())

    # The name persists across requests while the app runs and is forgotten when memory is
    # cleared, which is the "never saved" promise.
    def test_names_survive_between_calls_but_not_a_cleared_memory(self):
        app.redact(RESUME, learn=True)
        self.assertEqual(app.redact("Parkhurst"), "[NAME]")
        app._known_terms.clear()
        self.assertEqual(app.redact("Parkhurst"), "Parkhurst")

    # Words listed in the REDACT_TERMS setting (a school or employer, say) are removed, even with
    # extra spaces or different capitalization.
    def test_extra_terms_from_settings_are_removed(self):
        with mock.patch.object(app, "EXTRA_TERMS", ["Fairview High", "Indigo BioAutomation"]):
            out = app.redact("Aide at fairview   high and an intern at Indigo BioAutomation.")
        self.assertEqual(out, "Aide at [NAME] and an intern at [NAME].")

    # KNOWN LIMITATION (marked expectedFailure): a two-word job title such as "Software Engineer"
    # on the first line is learned as a name. It shows as 'x' in the results; remove the decorator
    # once the bug is fixed.
    @unittest.expectedFailure
    def test_job_title_on_first_line_is_not_mistaken_for_a_name(self):
        # KNOWN LIMITATION: a two-word title such as "Software Engineer" at the top is treated as a name,
        # which then blanks the words "software" and "engineer" everywhere. Remove expectedFailure once fixed.
        app.redact("Software Engineer\njo@example.com\nBuilt web apps", learn=True)
        self.assertEqual(app.redact("I am a software engineer"), "I am a software engineer")


# COUNTS AND THE ON/OFF SWITCH: the per-type counts shown in the "items removed" badge, the
# INTERVIEW_REDACT=off switch, and a whole-résumé check.
class TestCountsAndSwitch(RedactTestCase):
    # The per-type counts behind the "items removed" badge are right (both links are counted).
    def test_counts_by_type(self):
        counts = {}
        app.redact(RESUME, learn=True, counts=counts)
        for k in ("EMAIL", "PHONE", "LINK", "ADDRESS", "LOCATION", "NAME", "DATE OF BIRTH"):
            self.assertIn(k, counts)
        self.assertEqual(counts["EMAIL"], 1)
        self.assertEqual(counts["LINK"], 2)

    # Ordinary text produces an empty count.
    def test_counts_stay_empty_when_nothing_is_found(self):
        counts = {}
        app.redact("Built a REST API in Python.", counts=counts)
        self.assertEqual(counts, {})

    # With INTERVIEW_REDACT=off the text comes back unchanged.
    def test_redaction_can_be_switched_off(self):
        with mock.patch.object(app, "REDACT", False):
            self.assertEqual(app.redact("jo@example.com"), "jo@example.com")

    # Every personal detail in the sample résumé is gone, while the useful content ("Help Desk
    # Aide") remains.
    def test_full_resume_has_no_leftover_pii(self):
        out = app.redact(RESUME, learn=True)
        for bad in PII:
            self.assertNotIn(bad, out)
        self.assertIn("Help Desk Aide", out)  # the useful part is still there


class FakeLLM:
    """Stands in for call_llm: records every prompt and returns canned JSON."""

    def __init__(self, reply=None):
        self.prompts = []
        self.reply = reply if reply is not None else {
            "questions": [{"type": "technical", "q": "Q1"}, {"type": "weird", "q": "Q2"}, {"q": ""}, "junk"],
            "scores": {"situation": 9, "task": -3, "action": "4", "result": None},
            "strengths": ["s"], "improvements": ["i"], "coach_question": "?",
            "summary": "overall", "priorities": ["p"], "next_steps": ["n"]}

    def __call__(self, prompt):
        self.prompts.append(prompt)
        return json.dumps(self.reply)


# WHAT IS SENT TO THE AI: call_llm is replaced by a fake that records each prompt, so these tests
# prove what would leave the computer, and check how model replies are cleaned up.
class TestPrompts(RedactTestCase):
    def setUp(self):
        super().setUp()
        self.llm = FakeLLM()
        p = mock.patch.object(app, "call_llm", self.llm)
        p.start(); self.addCleanup(p.stop)

    def assertNoPII(self, prompt):
        for bad in PII:
            self.assertNotIn(bad, prompt, f"{bad!r} leaked into the prompt")

    # The résumé and job description (extra email, phone and address) are clean in the question-
    # writing prompt, and useful content stays.
    def test_questions_prompt_is_clean(self):
        app.make_questions({"role": "IT Support", "resume": RESUME, "jd": "Email hr@acme.com or 765-555-0199. 400 Oak Ave, Dayton, OH 45402"})
        sent = self.llm.prompts[0]
        self.assertNoPII(sent)
        for bad in ("hr@acme.com", "765-555-0199", "Oak Ave", "45402"):
            self.assertNotIn(bad, sent)
        self.assertIn("Help Desk Aide", sent)

    # A name learned from the résumé is removed from a typed answer, along with an email and phone
    # number inside it.
    def test_feedback_prompt_removes_name_learned_from_resume(self):
        app.make_questions({"role": "IT", "resume": RESUME})
        app.make_feedback({"role": "IT", "question": "Tell me about a time",
                           "answer": "I'm Logan Parkhurst. Text me on 812-555-0142 or jo@example.com about the printer fix."})
        sent = self.llm.prompts[-1]
        self.assertNoPII(sent)
        self.assertNotIn("812-555-0142", sent)
        self.assertIn("printer fix", sent)

    # The end-of-session prompt is clean too, including the earlier strengths and improvement
    # notes.
    def test_summary_prompt_is_clean_including_coach_notes(self):
        app.make_questions({"role": "IT", "resume": RESUME})
        app.make_summary({"role": "IT", "items": [{
            "question": "Q", "answer": "Logan here, jo@example.com", "scores": {"situation": 3},
            "strengths": ["Parkhurst was clear"], "improvements": ["email jo@example.com less"]}]})
        sent = self.llm.prompts[-1]
        self.assertNoPII(sent)
        self.assertNotIn("jo@example.com", sent)

    # With redaction off, the prompt contains the text exactly as written.
    def test_nothing_is_redacted_when_switched_off(self):
        with mock.patch.object(app, "REDACT", False):
            app.make_feedback({"role": "IT", "question": "Q", "answer": "mail jo@example.com"})
        self.assertIn("jo@example.com", self.llm.prompts[-1])

    # Junk entries from the model are dropped, an unknown type becomes "behavioral", and n limits
    # how many questions come back.
    def test_questions_are_cleaned_up_and_capped(self):
        out = app.make_questions({"role": "IT", "n": 5})
        self.assertEqual(out["questions"], [{"type": "technical", "q": "Q1"}, {"type": "behavioral", "q": "Q2"}])
        self.assertEqual(len(app.make_questions({"role": "IT", "n": 1})["questions"]), 1)

    # An empty question list from the model gives a clear error.
    def test_no_usable_questions_is_an_error(self):
        self.llm.reply = {"questions": []}
        with self.assertRaises(app.LLMError):
            app.make_questions({"role": "IT"})

    # Out-of-range or odd scores are fixed: 9 becomes 5, -3 becomes 1, "4" becomes 4 and missing
    # becomes 1.
    def test_feedback_scores_are_clamped_to_1_through_5(self):
        sc = app.make_feedback({"role": "IT", "question": "Q", "answer": "A"})["scores"]
        self.assertEqual(sc, {"situation": 5, "task": 1, "action": 4, "result": 1})

    # No answers to summarise, or an empty summary from the model, is an error.
    def test_summary_needs_items_and_text(self):
        with self.assertRaises(app.LLMError):
            app.make_summary({"items": []})
        self.llm.reply = {"summary": ""}
        with self.assertRaises(app.LLMError):
            app.make_summary({"items": [{"question": "Q", "answer": "A"}]})

    # The "NEVER write a model answer" rule (coach, not answer machine) stays in the feedback
    # prompt.
    def test_prompts_tell_the_model_not_to_write_answers(self):
        app.make_feedback({"role": "IT", "question": "Q", "answer": "A"})
        self.assertIn("NEVER write a model answer", self.llm.prompts[-1])


# READING THE MODEL'S REPLY: pulling a JSON object out of whatever text the model returns.
class TestAskJson(unittest.TestCase):
    # JSON wrapped in "Sure!" and a code fence is still parsed.
    def test_json_inside_code_fence_or_chatter(self):
        with mock.patch.object(app, "call_llm", return_value='Sure!\n```json\n{"a": 1}\n```'):
            self.assertEqual(app.ask_json("x"), {"a": 1})

    # A reply with no JSON, such as a refusal, gives a clean error.
    def test_reply_without_json_is_an_error(self):
        with mock.patch.object(app, "call_llm", return_value="I cannot help with that"):
            with self.assertRaises(app.LLMError):
                app.ask_json("x")

    # Malformed JSON gives a clean error.
    def test_broken_json_is_an_error(self):
        with mock.patch.object(app, "call_llm", return_value="{not json}"):
            with self.assertRaises(app.LLMError):
                app.ask_json("x")


# RÉSUMÉ FILE READING: turning an uploaded .txt, .md or .docx file into plain text.
class TestExtractText(unittest.TestCase):
    @staticmethod
    def make_docx(paragraphs):
        body = "".join(f"<w:p><w:r><w:t>{p}</w:t></w:r></w:p>" for p in paragraphs)
        xml = f'<?xml version="1.0"?><w:document xmlns:w="x"><w:body>{body}</w:body></w:document>'
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("word/document.xml", xml)
        return buf.getvalue()

    # Plain text and Markdown are read, accents intact, and the extension check ignores case.
    def test_txt_and_md(self):
        self.assertEqual(app.extract_text("r.txt", "héllo".encode()), "héllo")
        self.assertEqual(app.extract_text("R.MD", b"# hi"), "# hi")

    # A Word file keeps its line breaks and turns &amp; back into &.
    def test_docx_keeps_paragraph_breaks_and_unescapes(self):
        text = app.extract_text("r.docx", self.make_docx(["Tom &amp; Jerry", "Second line"]))
        self.assertEqual(text.strip().splitlines(), ["Tom & Jerry", "Second line"])

    # An unsupported file type (.exe) is refused with a message.
    def test_unsupported_type_is_an_error(self):
        with self.assertRaises(app.LLMError):
            app.extract_text("r.exe", b"x")

    # A corrupt .docx fails loudly instead of returning junk text.
    def test_bad_docx_raises_instead_of_returning_garbage(self):
        with self.assertRaises(Exception):
            app.extract_text("r.docx", b"not a zip")


# ERROR MESSAGES: failures talking to Anthropic or Ollama should produce a clear, actionable
# message instead of a crash.
class TestCallLlmErrors(unittest.TestCase):
    # Choosing Anthropic with no key set names ANTHROPIC_API_KEY in the error.
    def test_missing_key_has_a_clear_message(self):
        with mock.patch.object(app, "PROVIDER", "anthropic"), mock.patch.object(app, "KEY", ""):
            with self.assertRaises(app.LLMError) as cm:
                app.call_llm("hi")
        self.assertIn("ANTHROPIC_API_KEY", str(cm.exception))

    # An INTERVIEW_PROVIDER other than anthropic or ollama is rejected.
    def test_unknown_provider(self):
        with mock.patch.object(app, "PROVIDER", "nope"):
            with self.assertRaises(app.LLMError):
                app.call_llm("hi")

    # A refused connection produces a message that mentions Ollama.
    def test_ollama_not_running(self):
        with mock.patch.object(app, "PROVIDER", "ollama"), \
                mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError(ConnectionRefusedError())):
            with self.assertRaises(app.LLMError) as cm:
                app.call_llm("hi")
        self.assertIn("Ollama", str(cm.exception))

    # A 404 from Ollama tells the user to run "ollama pull <model>".
    def test_ollama_missing_model_tells_you_the_pull_command(self):
        err = urllib.error.HTTPError("u", 404, "nf", {}, io.BytesIO(b'{"error": "model not found"}'))
        with mock.patch.object(app, "PROVIDER", "ollama"), mock.patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaises(app.LLMError) as cm:
                app.call_llm("hi")
        self.assertIn("ollama pull", str(cm.exception))

    # A 401 from the Anthropic API becomes "Your API key was rejected".
    def test_anthropic_bad_key(self):
        err = urllib.error.HTTPError("u", 401, "no", {}, io.BytesIO(b'{"error": {"message": "invalid x-api-key"}}'))
        with mock.patch.object(app, "PROVIDER", "anthropic"), mock.patch.object(app, "KEY", "k"), \
                mock.patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaises(app.LLMError) as cm:
                app.call_llm("hi")
        self.assertIn("API key was rejected", str(cm.exception))


# THE REAL SERVER: starts the actual HTTP handler on a free local port (127.0.0.1 only) and sends
# it real requests.
class TestServer(unittest.TestCase):
    """Starts the real HTTP handler on a free port (127.0.0.1 only) and talks to it."""

    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown(); cls.httpd.server_close()

    def setUp(self):
        app._known_terms.clear()
        self.addCleanup(app._known_terms.clear)
        p = mock.patch.object(app, "REDACT", True)
        p.start(); self.addCleanup(p.stop)

    def call(self, path, body=None, headers=None, method=None):
        h = {"Content-Type": "application/json"}
        h.update(headers if headers is not None else {"X-Requested-With": "interview-coach"})
        data = json.dumps(body).encode() if isinstance(body, (dict, list)) else body
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", data, h, method=method)
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")

    # /api/config returns exactly provider, model, ready and redact.
    def test_config_reports_provider_and_redaction_state(self):
        status, j = self.call("/api/config", headers={})
        self.assertEqual(status, 200)
        self.assertEqual(set(j), {"provider", "model", "ready", "redact"})
        self.assertIs(j["redact"], True)

    # /api/redact returns the cleaned text, per-type counts and an enabled flag, with no personal
    # details left.
    def test_redact_endpoint_returns_text_counts_and_enabled(self):
        status, j = self.call("/api/redact", {"learn": True, "text": RESUME})
        self.assertEqual(status, 200)
        self.assertTrue(j["enabled"])
        for bad in PII:
            self.assertNotIn(bad, j["text"])
        self.assertEqual(j["counts"]["EMAIL"], 1)

    # The name carryover check done by hand in PowerShell, automated: learn from the résumé, then
    # clean an answer.
    def test_name_learned_by_one_request_is_applied_to_the_next(self):
        self.call("/api/redact", {"learn": True, "text": RESUME})
        _, j = self.call("/api/redact", {"text": "I'm Logan Parkhurst, jo@example.com"})
        self.assertEqual(j["text"], "I'm [NAME], [EMAIL]")

    # A POST without X-Requested-With gets 403, which stops other websites from spending your API
    # credit.
    def test_post_without_the_custom_header_is_refused(self):
        status, _ = self.call("/api/redact", {"text": "x"}, headers={})
        self.assertEqual(status, 403)

    # A request whose Host header is not localhost or 127.0.0.1 gets 403 (DNS-rebinding
    # protection).
    def test_requests_with_a_foreign_host_header_are_refused(self):
        status, _ = self.call("/api/config", headers={"Host": "evil.example"})
        self.assertEqual(status, 403)

    # An unknown endpoint returns 404.
    def test_unknown_path_is_404(self):
        self.assertEqual(self.call("/api/nope", {})[0], 404)

    # An oversized upload returns 413.
    def test_too_large_body_is_rejected(self):
        with mock.patch.object(app, "MAX_BODY", 10):
            status, _ = self.call("/api/redact", {"text": "x" * 100})
        self.assertEqual(status, 413)

    # Garbage input returns 400 with an error message and the server keeps running.
    def test_bad_json_is_a_400_not_a_crash(self):
        status, j = self.call("/api/redact", b"{not json")
        self.assertEqual(status, 400)
        self.assertIn("error", j)

    # A full /api/questions call works with a fake model, and the email never reaches the prompt.
    def test_questions_endpoint_end_to_end_with_fake_model(self):
        llm = FakeLLM()
        with mock.patch.object(app, "call_llm", llm):
            status, j = self.call("/api/questions", {"role": "IT", "resume": RESUME, "n": 2})
        self.assertEqual(status, 200)
        self.assertEqual(len(j["questions"]), 2)
        self.assertNotIn("logan.parkhurst@example.com", llm.prompts[0])

    # When the model call fails, the server returns 502 with the error message.
    def test_model_failure_becomes_a_502_with_the_message(self):
        with mock.patch.object(app, "call_llm", side_effect=app.LLMError("model is down")):
            status, j = self.call("/api/feedback", {"role": "IT", "question": "Q", "answer": "A"})
        self.assertEqual((status, j["error"]), (502, "model is down"))

    # Uploading a .txt file to /api/extract returns its text.
    def test_extract_endpoint_reads_a_text_file(self):
        status, j = self.call("/api/extract", b"hello resume", headers={
            "X-Requested-With": "interview-coach", "X-Filename": "r.txt", "Content-Type": "application/octet-stream"})
        self.assertEqual((status, j["text"]), (200, "hello resume"))


if __name__ == "__main__":
    unittest.main()