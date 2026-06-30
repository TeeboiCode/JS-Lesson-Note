#!/usr/bin/env python3
"""Rebuild index.html with fundamentals-before-DOM curriculum order."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
INDEX = ROOT / "index.html"
FRAG = ROOT / "fragments"

def read_frag(name):
    return (FRAG / name).read_text(encoding="utf-8")

def extract_sections(content):
    pattern = r'(      <!-- ═+[\s\S]*?      <section class="lesson" id="(\w+)">[\s\S]*?      </section>)'
    sections = {}
    for full, sid in re.findall(pattern, content):
        sections[sid] = full
    return sections

def renumber_section(section, num, title_sub=None):
    section = re.sub(
        r'<div class="lesson-num">Lesson \d+</div>',
        f'<div class="lesson-num">Lesson {num:02d}</div>',
        section,
        count=1,
    )
    if title_sub:
        section = re.sub(
            r'<span class="subtitle">[^<]*</span>',
            f'<span class="subtitle">{title_sub}</span>',
            section,
            count=1,
        )
    return section

def add_present_quiz_button(section):
    """Add present quiz button if quiz block exists but button missing."""
    if 'btn-present-quiz' in section:
        return section
    return section.replace(
        '<div class="exercise-block quiz"',
        '<div class="exercise-block quiz"',
    ).replace(
        '<p>Select the best answer',
        '<button type="button" class="btn-present-quiz" onclick="presentQuiz(this)">📸 Present Quiz for Screenshot</button>\n          <p>Select the best answer',
        1,
    ) if 'exercise-block quiz' in section else section

def enhance_variables(section):
    scope = read_frag("scope-supplement.html")
    # Insert scope before hr before exercises
    if "JavaScript Scope" not in section:
        section = section.replace(
            '<hr class="section-divider" />',
            scope + '\n        <hr class="section-divider" />',
            1,
        )
    # Update title
    section = re.sub(
        r'<h2>Variables, Operators &amp; Data Types</h2>',
        '<h2>Variables &amp; Scope</h2>',
        section,
    )
    section = re.sub(
        r'<span class="subtitle">Storing data and performing calculations</span>',
        '<span class="subtitle">var, let, const, operators, and scope</span>',
        section,
    )
    # Remove duplicate primitive block heading if we have full data lesson - keep operators
    return section

def enhance_functions(section):
    drills = read_frag("function-exercises.html")
    if "Function Drills" not in section:
        section = section.replace(
            '<hr class="section-divider" />',
            drills + '\n        <hr class="section-divider" />',
            1,
        )
    section = re.sub(
        r'<h2>Functions &amp; Form Validation</h2>',
        '<h2>JavaScript Functions</h2>',
        section,
    )
    section = re.sub(
        r'<span class="subtitle">Reusable code blocks and real-world form handling</span>',
        '<span class="subtitle">Declarations, arrows, parameters, callbacks</span>',
        section,
    )
    return section

def trim_objects_to_objects_only(section):
    """Keep objects/JSON, remove array-heavy parts (now in arrays lesson)."""
    section = re.sub(
        r'<h2>Objects and Arrays</h2>',
        '<h2>Objects &amp; Form Validation</h2>',
        section,
    )
    section = re.sub(
        r'<span class="subtitle">Organizing and working with collections of data</span>',
        '<span class="subtitle">Objects, JSON, and validating forms</span>',
        section,
    )
    # Remove array-focused h3 blocks - keep What Is an Object through JSON
    # Remove "What Is an Array?" through "Looping Through Objects and Arrays" array parts
    for heading in [
        r'<h3>What Is an Array\?</h3>[\s\S]*?<h3>Looping Through Objects and Arrays</h3>',
        r'<h3>Essential Array Methods</h3>[\s\S]*?(?=<h3>Looping)',
    ]:
        section = re.sub(heading, '', section)
    return section

def build_sidebar():
    links = [
        ("intro", "01", "Introduction to JavaScript"),
        ("syntax", "02", "Language and Syntax"),
        ("output", "03", "Output: alert, prompt, console"),
        ("data", "04", "Data &amp; Types"),
        ("variables", "05", "Variables &amp; Scope"),
        ("boolean", "06", "Boolean Logic"),
        ("functions", "07", "JavaScript Functions"),
        ("arrays", "08", "JavaScript Arrays"),
        ("todo", "09", "Todo List Project"),
        ("control", "10", "Conditionals &amp; Looping"),
        ("dom", "11", "Document &amp; Browser Objects"),
        ("events", "12", "Event-driven Programming"),
        ("objects", "13", "Objects &amp; Form Validation"),
    ]
    nav = ['      <div class="nav-section">Part 1 — JavaScript Core</div>']
    for i, (hid, num, label) in enumerate(links[:10]):
        nav.append(
            f'      <a class="nav-link" href="#{hid}"'
            f'\n        ><span class="nav-num">{num}</span> {label}</a'
            f'\n      >'
        )
    nav.append('      <div class="nav-section">Part 2 — Browser &amp; DOM</div>')
    for hid, num, label in links[10:]:
        nav.append(
            f'      <a class="nav-link" href="#{hid}"'
            f'\n        ><span class="nav-num">{num}</span> {label}</a'
            f'\n      >'
        )
    return "\n".join(nav)

def build_hero():
    return """        <div class="hero-meta">
          <div class="meta-item">
            <span class="meta-label">Chapters</span>
            <span class="meta-value">13</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Level</span>
            <span class="meta-value">Beginner</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Exercises</span>
            <span class="meta-value">26+</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Quizzes</span>
            <span class="meta-value">65 Questions</span>
          </div>
        </div>"""

MODAL_AND_SCRIPT = '''
    <div class="quiz-modal-overlay" id="quiz-modal-overlay" onclick="if(event.target===this)closeQuizModal()">
      <div class="quiz-modal" id="quiz-modal">
        <button class="quiz-modal-close" onclick="closeQuizModal()" title="Close">&times;</button>
        <div class="quiz-modal-header">
          <h3 id="quiz-modal-title">Quiz</h3>
          <p>Write your answers (A, B, C, or D) in your notebook. We'll solve together after.</p>
        </div>
        <div id="quiz-modal-body"></div>
        <div class="quiz-modal-footer">Tip: Screenshot this screen to share with students.</div>
      </div>
    </div>

    <button
      id="scrolltop"
      onclick="window.scrollTo({ top: 0, behavior: 'smooth' })"
      title="Back to top"
    >
      ↑
    </button>

    <script>
      function presentQuiz(btn) {
        const quizBlock = btn.closest(".exercise-block.quiz");
        const title = quizBlock.querySelector("h5").textContent;
        const questions = quizBlock.querySelectorAll(".quiz-question");
        const letters = ["A", "B", "C", "D"];
        let html = "";

        questions.forEach((q, qi) => {
          const qText = q.querySelector(".quiz-q").innerHTML;
          const options = q.querySelectorAll(".quiz-options li label");
          html += '<div class="quiz-present-item">';
          html += "<p>" + qText + "</p><ul class=\\"quiz-present-options\\">";
          options.forEach((opt, oi) => {
            const text = opt.textContent.trim();
            html += '<li><span class="letter">' + letters[oi] + ".</span> " + text + "</li>";
          });
          html += "</ul></div>";
        });

        document.getElementById("quiz-modal-title").textContent = title;
        document.getElementById("quiz-modal-body").innerHTML = html;
        document.getElementById("quiz-modal-overlay").classList.add("open");
        document.body.style.overflow = "hidden";
      }

      function closeQuizModal() {
        document.getElementById("quiz-modal-overlay").classList.remove("open");
        document.body.style.overflow = "";
      }

      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeQuizModal();
      });

      const progress = document.getElementById("progress");
      window.addEventListener("scroll", () => {
        const scrollTop = window.scrollY;
        const docHeight = document.body.scrollHeight - window.innerHeight;
        progress.style.width = (scrollTop / docHeight) * 100 + "%";

        document
          .getElementById("scrolltop")
          .classList.toggle("visible", scrollTop > 400);

        const sections = document.querySelectorAll(".lesson");
        const links = document.querySelectorAll(".nav-link");
        sections.forEach((s, i) => {
          const rect = s.getBoundingClientRect();
          if (rect.top <= 200 && rect.bottom >= 200) {
            links.forEach((l) => l.classList.remove("active"));
            if (links[i]) links[i].classList.add("active");
          }
        });
      });
    </script>'''

def main():
    content = INDEX.read_text(encoding="utf-8")
    sections = extract_sections(content)

    order = [
        "intro", "syntax",
        None,  # output - fragment
        None,  # data
        "variables",
        None,  # boolean
        "functions",
        None,  # arrays
        None,  # todo
        "control",
        "dom", "events",
        "objects",
    ]

    fragments = {
        2: read_frag("lesson-output.html"),
        3: read_frag("lesson-data.html"),
        5: read_frag("lesson-boolean.html"),
        7: read_frag("lesson-arrays.html"),
        8: read_frag("lesson-todo.html"),
    }

    built = []
    lesson_num = 1
    for i, key in enumerate(order):
        if key is None:
            sec = fragments[i]
        else:
            sec = sections[key]
            if key == "variables":
                sec = enhance_variables(sec)
            elif key == "functions":
                sec = enhance_functions(sec)
            elif key == "objects":
                sec = trim_objects_to_objects_only(sec)
            sec = add_present_quiz_button(sec)
        sec = renumber_section(sec, lesson_num)
        built.append(sec)
        lesson_num += 1

    # Extract head and hero start
    head_match = re.search(r'^[\s\S]*?<main id="main">', content)
    hero_start = head_match.group(0) if head_match else ""

    # Replace sidebar links
    sidebar_pattern = r'      <div class="nav-section">Chapters</div>[\s\S]*?      <a class="nav-link" href="#functions"[\s\S]*?</a\s*>'
    hero_start = re.sub(sidebar_pattern, build_sidebar(), hero_start)

    # Replace hero meta
    hero_start = re.sub(
        r'<div class="hero-meta">[\s\S]*?</div>\s*</div>\s*\n\s*<!-- ═',
        build_hero() + '\n      </div>\n\n      <!-- ═',
        hero_start,
        count=1,
    )

    # Update hero description
    hero_start = hero_start.replace(
        "5-question quiz with carefully crafted answer choices.",
        "hands-on exercises, 5-question quizzes, and a console Todo project — all before DOM.",
    )

    main_body = "\n\n".join(built)
    tail = MODAL_AND_SCRIPT + "\n  </body>\n</html>"

    output = hero_start + "\n" + main_body + "\n\n    </main>\n\n" + tail
    INDEX.write_text(output, encoding="utf-8")
    print(f"Rebuilt {INDEX} with {lesson_num - 1} lessons")

if __name__ == "__main__":
    main()
