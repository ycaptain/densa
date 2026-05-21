---
type: source
domain: research-papers
authors: ["Alessandro Vanzo", "Sankalan Pal Chowdhury", "Mrinmaya Sachan"]
affiliation: "ETH Zürich, Department of Computer Science"
published: 2024-09-24
venue: "arXiv preprint (cs.CY)"
arxiv_id: "2409.15981"
doi: "10.48550/arXiv.2409.15981"
tags: [llm-tutoring, rct, k12, language-learning, homework, gpt-4, esl]
status: active
source_url: "https://arxiv.org/abs/2409.15981"
source_html_url: "https://arxiv.org/html/2409.15981v1"
retrieved: 2026-05-21
---

# GPT-4 as a Homework Tutor can Improve Student Engagement and Learning Outcomes

> [!note] Source provenance
> Full text retrieved from arXiv HTML (v1) at
> `https://arxiv.org/html/2409.15981v1` on 2026-05-21. The PDF version
> of record is at `https://arxiv.org/abs/2409.15981`. License: arXiv
> non-exclusive distribution. Inline citation links (`[N]`) in the
> body point to the paper's reference list, reproduced in
> `## References` below.

**Authors.** Alessandro Vanzo, Sankalan Pal Chowdhury, Mrinmaya Sachan
(ETH Zürich, Department of Computer Science).
**Submitted.** 24 September 2024.
**arXiv.** [2409.15981](https://arxiv.org/abs/2409.15981) (cs.CY).

## Abstract

This work contributes to the scarce empirical literature on
LLM-based interactive homework in real-world educational settings
and offers a practical, scalable solution for improving homework in
schools. Homework is an important part of education in schools
across the world, but in order to maximize benefit, it needs to be
accompanied with feedback and followup questions. We developed a
prompting strategy that enables GPT-4 to conduct interactive
homework sessions for high-school students learning English as a
second language. Our strategy requires minimal efforts in content
preparation, one of the key challenges of alternatives like home
tutors or ITSs. We carried out a Randomized Controlled Trial (RCT)
in four high-school classes, replacing traditional homework with
GPT-4 homework sessions for the treatment group. We observed
significant improvements in learning outcomes, specifically a
greater gain in grammar, and student engagement. In addition,
students reported high levels of satisfaction with the system and
wanted to continue using it after the end of the RCT.

**Keywords.** Homework, Tutoring, Language Education, Randomized
Control Trial, GPT-4.

## 1. Introduction

Homework is an important component of education as it helps
students self evaluate and develop self regulation skills (Ramdass
and Zimmerman, 2011). However, in order to fully benefit from
solving homework problems, it is important that students receive
swift feedback on their work (Schartel, 2012), which is not
possible for teachers due to time constraints. This leads to
several students having to resort to private tutors, which can be
prohibitively expensive for several households (Campani, 2013). In
this work we look at the possibility of leveraging GPT-4 (OpenAI
and Team, 2024) as a tutor to assist students in their homework
using a simple prompting strategy and an interface we developed.

In the seminal paper on the 2 Sigma problem, Bloom (1984) noted
that compared to conventional learning, which consists of lectures
followed by evaluation tests, students who received feedback on
said tests and were given corrective instruction thereafter
performed one standard deviation (σ) higher in terms of learning
gains. The same paper notes a 0.8σ improvement for graded
homework, but only a 0.3σ improvement if the homework is simply
assigned without follow-up. The maximum benefit comes from
one-on-one or one-on-few tutoring at 2σ but Bloom found no
substitute for it. The status quo in schools roughly corresponds to
the scenario where homework is never graded or, if graded, is done
superficially. While the development of MOOCs with online lecture
videos has extended the benefits of conventional education to
larger populations (Ferguson and Sharples, 2014), most MOOCs still
lack proper homework feedback or corrective instruction. Attempts
have been made to try to scale the benefits of feedback and
corrective instruction with the use of peer-tutoring (Cohen et al.,
1982) and Intelligent Tutoring Systems (Nwana, 1990) but these too
have problems with effectiveness and scaling.

Recent developments in Large Language Models (LLMs) (OpenAI and
Team, 2024; Team, 2024; Touvron et al., 2023) have opened up the
possibility of leveraging them for interactive homework and
corrective feedback (Kasneci et al., 2023). The rapid development
and adoption of LLMs like GPT-4 have provided the educational
community with several new opportunities as well as challenges.
While the benefits of GPT models in education are well studied
(Baidoo-Anu and Ansah, 2023), educators are also concerned by the
potential use of GPT as a tool for plagiarism in homeworks
(Dehouche, 2021) and them causing an overdependence by students
(Zhai et al., 2024). These fears are further exacerbated by the
prevalence of hallucinations (Chelli et al., 2024) and jailbreaks
(Chu et al., 2024). Studies involving real-world situations are,
therefore, extremely important.

Therefore, in this paper, we summarize our observations and
learnings from testing out the effects of replacing static homework
with a GPT-4 instance which has been instructed to cover the
material of the homework, but in an interactive manner. Our
intervention fills a gap that exists in many school systems without
having to cause disruption to existing educational systems. We
carry out a Randomized Control Trial (RCT) in an Italian high
school to understand if such an intervention is indeed beneficial
to students, both in terms of the students' self-assessments and
also in terms of externally measured learning gains. We find that
students who used GPT-4 in this manner have limited improvements in
learning gain, while also feeling better supported in terms of
available resources. Finally, all students who would still be in
school after the conclusion of the study indicated that they would
want to continue to have access to the tutor, giving us hope that
despite the contemporary fears that LLMs may lead to the decline of
homework in education, LLMs can also be used to make homework more
fun and didactically useful to students.

## 2. Background

Educational research has consistently shown that personalized
tutoring is one of the most effective forms of instruction.
However, scaling this approach has been a significant challenge.
In recent years, advances in artificial intelligence, particularly
through Large Language Models (LLMs) like GPT-4, have sparked
interest in their potential to provide scalable, interactive
tutoring solutions. Despite early successes, the use of LLMs in
education has raised important questions around their efficacy,
potential risks, and best practices for implementation.

In this section, we first explore the history and limitations of
scaling tutoring using traditional methods and Intelligent
Tutoring Systems (ITS). We then discuss the rise of LLMs and their
application in education, focusing on their strengths and potential
challenges. Finally, we review recent empirical studies that have
evaluated LLM-based tutoring systems, highlighting both the promise
and the gaps in the current literature, which our study aims to
address.

### 2.1. The Challenge of Scaling Tutoring in Education

In Bloom's seminal work on the "2 Sigma Problem" (Bloom, 1984), it
was shown that students who received personalized tutoring
performed two standard deviations better than those in traditional
classroom settings. However, scaling one-on-one tutoring to large
student populations is challenging due to the high cost and
resource demands. Intelligent Tutoring Systems (ITS) attempt to
fill this gap, promising to offer personalized, scalable
instruction (Nwana, 1990). Yet, while ITS can help improve learning
outcomes, they face challenges in terms of scalability, content
preparation, and flexibility (Cai et al., 2019).

### 2.2. The Role of Large Language Models in Education

The advent of Large Language Models (LLMs) such as GPT-4 (OpenAI
and Team, 2024) represents a potential breakthrough in addressing
the issue of scalability in tutoring. Unlike traditional ITSs,
which require extensive manual content creation, LLMs can generate
interactive and dynamic educational content with minimal human
intervention. Research suggests that LLMs like GPT-4 can mimic
tutor-like behavior by engaging in natural language dialogues,
providing feedback, and offering corrective instruction, all of
which are key components of effective tutoring (Kasneci et al.,
2023).

Despite their promise, the use of LLMs in education has sparked
mixed reactions. On one hand, proponents argue that LLMs could
offer an affordable and scalable tutoring solution, especially for
students in under-resourced educational settings. Yet, many
educators also express concern about issues like student
over-reliance on AI tools, the risk of plagiarism, and the tendency
of LLMs to hallucinate or provide incorrect information (Dehouche,
2021; Zhai et al., 2024; Chelli et al., 2024). Given these
conflicting perspectives, empirical evidence from real-world
classroom settings is critical to assess whether LLMs can truly
enhance learning while mitigating potential risks.

### 2.3. Empirical Studies on LLMs in Feedback and Interactive Exercises

Several recent studies have begun exploring the effectiveness of
LLMs and LLM-based systems, particularly in higher education and
STEM fields (Padiyath et al., 2024; Tanay et al., 2024; Aruleba et
al., 2023; Krupp et al., 2023; Odekeye et al., n.d.). A large
volume of this work has focused on LLM-based agents for
programming support (Yang et al., 2024; Qi et al., 2024; Liffiton
et al., 2023; Kazemitabaar et al., 2024; Jacobs and Jaschke, 2024;
Liu et al., 2024; Lyu et al., 2024; Li et al., 2024; Choudhuri et
al., 2023; Pankiewicz and Baker, 2024). However, most studies in
this domain are limited to university-level computer science
courses, and few offer rigorous control conditions for comparison.

Outside of computer science, a growing body of work has evaluated
LLMs in domains like mathematics (Chowdhury et al., 2024;
Butgereit et al., 2023; Pardos and Bhandari, 2024), language
learning (Polakova and Klimova, 2024; Park et al., 2024), health
sciences (Kavadella et al., 2024; Chheang et al., 2024; Wang et
al., 2024), and other domains (Schmucker et al., 2024; Thway et
al., 2024; Chen and Chang, 2024; Zhang et al., 2024). However,
these studies often focus on highly structured tasks, such as
answering specific questions or performing well-defined
problem-solving activities, where the risks of misinformation are
relatively low.

### 2.4. Our Contributions

Despite the numerous studies published in this field, we note that
the literature on non-computer science subjects is still limited.
In particular, empirical studies in primary and secondary schools
are very few. We further note that there has been very little work
involving school-aged students and none of these gave their system
the flexibility that we grant GPT-4 with our strategy. The
scarcity of studies does not necessarily imply a scarcity of
potential for LLM-based technologies in this area. The potential
of these models in schools is significant, largely untapped and
well worth investigating.

Our work contributes to the understanding of the effectiveness and
applicability of LLMs as tutors in schools. We contribute to the
scarce literature on non-computer science subjects, and in
particular to the even scarcer empirical literature. To the best of
our knowledge, our work is the first in-field RCT incorporating a
recent, state-of-the-art LLM as a tutor for language learning in a
school. Our design is:

1. **Non-disruptive:** We intervene in the area of homework which
   has little involvement from the school system, via a prompting
   strategy needing no extra work from the teachers, thereby
   smoother adoption into the existing system.
2. **Context Aware:** Our prompt informs GPT of what the teacher
   expects the student to cover in the current homework,
   maintaining the teacher's freedom to decide the curriculum
   contents and speed.
3. **Adaptable:** We can adapt to a wide variety of different
   homework, from simple fill-in-the-blank grammar exercises to
   short essays on complex topics.
4. **Minimalistic:** We limit the level of engineering to prompt
   design, allowing for the possibility of using more powerful
   LLMs in the future.

We provide empirical insights into the potential of GPT-4 as a
tutor which can be leveraged and built upon by the community in
the future.

## 3. Methodology

We provide an overview of the study design in Figure 1. The
teacher, who assigns weekly homework exercises to students,
provides three key elements for each exercise: the **purpose**, a
brief informal description of the learning objectives; the
**description**, outlining the specific tasks students are asked to
complete; and an **example**, representing a typical instance of
the homework assignment. We prompt GPT-4 with these elements,
instructing it to generate an interactive exercise session aligned
with the original pedagogical goals. We test the effectiveness of
GPT-4 as a tutoring tool compared to traditional homework in a
randomized controlled trial (RCT). We assess student's learning
outcomes and engagement, using both external measures (pre- and
post-tests) and student feedback through questionnaires.

> Figure 1. Illustration of the study design. The teacher provides
> the weekly homework exercises. For each exercise the system
> collects three elements (purpose, description, example) and uses
> them to prompt GPT-4 to cover the same concepts and pedagogical
> purpose. The tutoring effectiveness is then tested as a
> replacement for standard homework in an RCT.

### 3.1. Participants

We conducted our study in a high school in Italy. The Italian high
school system, "scuola superiore," spans 5 years and includes
lyceums, technical institutes, and professional institutes.
Lyceums prepare students for university, technical institutes
offer career-oriented education, and professional institutes
provide vocational training.

We partnered with a technical institute, working with 4 classes,
all of whom were taught English by the same teacher. Two classes
were in the 3rd year (median student age 16) and two in the 5th
year (median age 18) on the tourism track, focusing on business
administration and foreign languages. The 3rd year classes
consisted of a total of 39 students, of which 20 (18 F and 2 M)
were assigned the control group while 19 (17 F and 2 M) were
assigned the treatment group. The 5th year consisted of 37
students, of which 19 (17 F and 2 M) were assigned to the control
group and 18 (13 F and 5 M) were assigned to the treatment group.
All the students had access to internet either through a smartphone
or through a computer.

### 3.2. Area of intervention

For every class, the English curriculum was composed of two main
parts: 3 hours of weekly lectures and 1-2 hours of weekly homework
and self-study. We intervened on homework and self-study.
Treatment group students were assigned interactive sessions with
GPT-4. Control group students were assigned the typical homework
they would have for the rest of the year. Treatment and control
group students attended the same lectures.

We note that the students of neither group were forbidden from
using ChatGPT on their own (almost two-thirds of Italian students
are likely to be using ChatGPT according to public reporting), so
any effects seen are *in addition to* that of self-usage.

### 3.3. Prompting Strategy

Figure 1 (left and centre panel) summarizes our prompting strategy.
Our goal is to give GPT-4 sufficient information in order to align
the homework with the expectations of the teacher, without
requiring any LLM-related expertise from the teacher or imposing
any additional workload on them. As such, we ask the teacher to
provide the following 3 components of the seed exercise:

1. **Exercise purpose:** the pedagogical purpose of the exercise,
   described in a few sentences.
2. **Exercise description:** a description of the task.
3. **Exercise example:** the exercise itself as it would be shown
   to the students.

We note that the teacher would need to prepare these for regular
homework anyway, and the only additional work is entering these to
the platform instead of disbursing it to the students. In
post-study feedback, the teacher claimed that while this change
introduced an initial learning curve for them, in the long term it
would reduce their workload somewhat.

Having obtained the seed exercise, we first ask GPT to generate a
step-by-step plan on how to carry out the homework. The final
prompt is obtained by appending the seed exercise and the
generated strategy to a generic Task Description. The LLM of our
choice was `gpt-4-0125-preview`. The interface was hosted on a
dedicated website that students could access with their own
personal devices outside of school hours.

We report the GPT-4 prompts for strategy generation and tutoring in
Appendix B. For the strategy generation, we provide the seed
exercise alongside a basic description of the tutoring task,
mentioning that we are working with high school students and
aiming at a B2 level of English according to the Common European
Framework of Reference for Languages (CEFR), and ask for an
appropriate tutoring strategy. In the tutoring prompt, we provide
a description of the tutoring task together with the seed exercise
and the generated strategy.

### 3.4. Randomized Controlled Trial

#### 3.4.1. Research Goals

Our primary focus is on how much the tool helped (or hindered)
student learning, and how the students felt about using the tool
both in the short and the long term. Beyond this, we also look at
their general outlook to the tool, how much they used it, and
which groups benefited more. We use a combination of external
measures (tests) and internal measures (questionnaires) to achieve
this, as detailed in the rest of this section.

#### 3.4.2. Intervention Design

We assigned students within each class to either the treatment or
the control condition using **stratified randomization** based on
their self-reported English GPA in the current year. The teacher
was not informed of the condition of the individual students, and
lectures were the same for all students. The students were
instructed not to share their group with her, to avoid
interference.

All students received weekly homework consisting of one or more
exercises, and the homework was carried out on a dedicated website
that students could access with their own devices, including
smartphones and computers. Students in the control group received
the homework as assigned by the teacher, in a format comparable to
the exercise they received outside of the experiment. They solved
each exercise individually and uploaded the answer on the online
platform. For each exercise assigned by the teacher, students in
the treatment group had access to a chat with GPT-4. In each chat,
the tutor used the prompt for the specific exercise. Students did
not see the original exercise from the teacher. In both treatment
and control conditions, students could access the platform at any
time. We did not enforce a minimum or maximum level of engagement.
The teacher could not observe the content of the student's
solution, but we informed her of who had submitted a solution for
each exercise. The intervention was planned to run for 6 weeks,
and was extended to 8 weeks due to delays in covering the required
content.

#### 3.4.3. Questionnaire design

Students completed one questionnaire before the beginning of the
intervention, one questionnaire per week during the intervention,
and one questionnaire after the end of the intervention. We refer
to these questionnaires as **initial questionnaire**, **weekly
questionnaire**, and **final questionnaire**, respectively. In
addition, students had to complete a **pre-test** and **post-test**
on the content covered during the intervention.

**Initial Questionnaire.** Given before the experimental
intervention. It asked the students to provide some contact
information and basic information about themselves (name, age,
email). We then included 9 background questions about the student
performance and motivation at school, some general and some
English-specific. We did not find a suitable standardized
questionnaire, so we developed these questions specifically for our
experiment. Afterwards, we included standardized questions on
self-efficacy at school. We selected the questions from Tuan et
al. (2005), translated them to Italian and applied some minor
adjustments to make them specific to English. This subsection
included 6 questions. We then included 6 questions about the
student experience with English homework, each question targeting
one of the 4 ARCS aspects (Li and Keller, 2018). While the ARCS
model was initially developed to guide the development of
education content, it is not uncommon to see questionnaires
targeting its 4 main aspects to assess the effectiveness of
educational contents. Finally, we included 6 questions assessing
the student experience during lectures, also targeting the ARCS
dimensions.

**Final Questionnaire.** Largely mirrored the initial
questionnaire. However, instead of asking about the experience of
students at school in general, it asked specifically about the
experience over the time the experimental intervention ran (2
months). In addition, we included questions for the treatment
group students asking feedback about the tutor.

**Weekly Questionnaire.** Three questions about the exercise
session as a whole and 2 questions for each exercise, using a
6-point Likert scale. In addition, for the treatment group, we
asked to report how the tutor was helpful giving the option to
select among a range of potential useful aspects.

**Pre-Test and Post-Test.** Both consisted of 24 multiple-choice
questions. We assigned 1 point for each question answered
correctly. The questions were provided to us by the teacher, who
designed 8 questions for each week of the intervention. For each
week, we randomized half of the questions to the pre-test and half
to the post-test. We report all questionnaires in Appendix.

## 4. Results and Analysis

We start off with some general statistics, and then proceed to
discuss each of our research questions in their own section.

### 4.1. General statistics

**Table 1. Usage statistics for the tutor**

|                                       | Third Year | Fifth Year | Total |
| ------------------------------------- | ---------- | ---------- | ----- |
| Control Group — # Assignments         | 195        | 97         | 292   |
| Control Group — Median HW Word Count  | 56         | 157        | 74    |
| Treatment Group — # Chats             | 199        | 93         | 292   |
| Treatment Group — Agent Messages (Md) | 15         | 12         | 14    |
| Treatment Group — User Messages (Md)  | 14         | 11         | 13    |
| Treatment — Words per Chat — Agent    | 977        | 1040       | 989   |
| Treatment — Words per Chat — User     | 114        | 314        | 143   |

#### 4.1.1. Participant Background

Table 2 reports the self-reported participant backgrounds. We note
that there is a slight overestimation of English ability on part of
the students, as more people consider themselves above average than
below average.

**Table 2. Self-reported previous performance by students**

|                                  | Third Year | Fifth Year | Total |
| -------------------------------- | ---------- | ---------- | ----- |
| Control — #Students              | 20         | 19         | 39    |
| Control — Mean Grade in English  | 7.20       | 7.54       | 7.37  |
| Control — Held Back in English   | 1          | 3          | 4     |
| Control — Below Average          | 4          | 7          | 11    |
| Control — Average                | 8          | 3          | 11    |
| Control — Above Average          | 8          | 9          | 17    |
| Treatment — #Students            | 19         | 18         | 36    |
| Treatment — Mean Grade English   | 7.63       | 7.43       | 7.53  |
| Treatment — Held Back English    | 0          | 1          | 1     |
| Treatment — Below Average        | 6          | 6          | 12    |
| Treatment — Average              | 5          | 5          | 10    |
| Treatment — Above Average        | 8          | 7          | 15    |

#### 4.1.2. Usage Statistics

Table 1 shows the overall usage summary of the platform. The 5th
year homework consisted of open questions on literature and
history, with several questions each week. The most common
behaviour among students was to write a somewhat complete answer.
The answer was then refined iteratively based on feedback from the
tutor, adding nuance, correcting grammar and including or fixing
factual information. The 3rd year homework consisted of
objective-type exercises (except for one essay-type exercise),
where the students were given sentences which they had to edit,
complete or transform according to the question, and there was
almost always a single correct answer. Student utterances for
these questions were most of the time just attempts at the right
answers, and not many students tried to have full conversations.

We segmented the conversations into a total of **1,549 questions**,
of which **940** (as judged by GPT-4o; counts may contain some
errors) were solved immediately by the students, while in **365**
cases the tutor revealed the answers. The conversations where a
reveal occurred were on average **4.7 utterances long**, which
would imply about 2 attempts by the student. Correct cases were
almost always 3 utterances long (Tutor-Student-Tutor) with the
exception of an exercise that required both the passive form and
the double object passive form which required 5 utterances.

#### 4.1.3. General Outlook

As a part of the final survey, students in the treatment group
were asked how they felt about the tutor. **32/33** respondents
thought that the tutor helped them with their homework, whereas
**30/35** felt that the tutor improved them on a practical level.
Further, **26/34** respondents felt that the tutor helped them keep
up with the English program. Most importantly, **32/35** overall
respondents wanted to continue using the tutor, with the 3 people
saying "No" all being in their last year of High School. This
shows that even in its current basic form, students enjoyed the
experience of using it.

### 4.2. Primary Analysis

In this section we present the primary observations of our study.
All variables (mentioned in italics) map to questions in one of our
questionnaires; for more details, see Appendix A.

#### 4.2.1. Overall Learning Gains

We start off by comparing overall learning gains of students in the
two conditions. To evaluate this, we conduct a one-sided *t*-test
and obtained a Cohen's *d* of 0.251 with a *p*-value of 0.314.
However, since the curricula for the 5th and 3rd years are
substantially different, resulting in a significant disparity in
score improvements between the two cohorts (*d* = 1.347,
*P* < 0.001), we perform distinct tests for each class. For 3rd
year the effect size is much larger favouring the treatment group,
and is marginally significant (***d* = 0.603, *P* = 0.087**). For
the 5th year, there is almost no difference (*d* = -0.004,
*P* = 0.991). We posit that this difference could emerge due to
the 5th year homework being essay-type compared to the 3rd year
homework being more objective with a single correct answer, which
could have led to the following 2 issues:

1. The lack of a clear correct answer would make 5th year answers
   harder to evaluate.
2. The pre- and post-test for both classes was objective type so
   the 5th year homework would have helped less in general.

Overall, given the limited nature of intervention, we can conclude
that under the right conditions, the treatment group does perform
better.

#### 4.2.2. Short Term Experience of Students

We had weekly questionnaires for the entire week and also at
exercise level. The week-level questionnaires asked students about
the *interestingness* and *usefulness* of their homework, while
the exercise-level questionnaires asked about the
*comprehensiveness* and *level_of_resources* of that particular
exercise. We observed that students in the treatment group gave
higher ratings in all 4 categories. Of these, *interestingness*
(*d* = 0.593, *P* = 0.011) and *level_of_resources* (*d* = 0.586,
*P* = 0.015) were significant but *usefulness* (*d* = 0.356,
*P* = 0.125) and *comprehensiveness* (*d* = 0.281, *P* = 0.234)
were not significant.

Further, the treatment group were asked what they liked about the
tutor, and **93%** of the times, the students picked at least one
option. The overall responses to this question are summarised in
Table 3.

**Table 3. Student responses to what they liked about each
exercise (treatment group only)**

| Useful Aspect                                        | Proportion |
| ---------------------------------------------------- | ---------- |
| The tutor's explanations                             | 63%        |
| Receiving feedback and corrections on my answers     | 57%        |
| Being guided step by step in the solution            | 45%        |
| Solving the exercise itself                          | 25%        |
| Other                                                | 0.42%      |
| **Percentage Marked At Least One**                   | **93%**    |
| Percentage Marked 2 Useful Aspects                   | 66%        |
| Percentage Marked 3 Useful Aspects                   | 29%        |
| Percentage Marked 4 or More Useful Aspects           | 3.8%       |

Overall, given the responses, we conclude that most of the students
found at least one facet of the tutor useful, making their overall
outlook positive.

#### 4.2.3. Long Term Experience of Students

Both the initial and final questionnaires included 22 questions
based on SESQ and ARCS frameworks (see Appendix A). Figure 2 shows
the average change in the students' responses to these between the
initial and final surveys (questions where a higher rating would be
more negative have had their signs reversed to make higher-is-
better for all questions).

We note that the differences in the two groups are not significant
for any of the questions (after correcting for FDR) but still
certain trends emerge. First of all, overall satisfaction increases
for both groups, but increases more for the treatment group.
Further, for all questions relating to homework (where we
intervened), the treatment group's opinions improved more than that
of the control group.

Another interesting trend that we notice is that **students'
confidence actually decreased for the treatment group**. One
possible reason might be that the students were mildly overconfident
in their ability to begin with, as is indicated by the
self-assessment of ability in English. However, since we did not
reassess ability in the final questionnaire, this is hard to
verify.

### 4.3. Secondary Analysis

In this section we investigate our data for the existence of
effects observed in previous research.

#### 4.3.1. Do stronger students benefit more?

Next, we look at the relation between initial skills of student and
how much they benefit. This is interesting because previous work
(Prather et al., 2024; Cipriano and Alves, 2024) suggests that
students with higher initial knowledge benefit more from GPT
tutoring. In order to evaluate this, we calculated the Pearson-R
and found that there was in fact a negative correlation
(***R* = -0.777, *P* < 0.001**) between *score_initial* and
*learning_gains* which is actually stronger than the control group
(*R* = -0.628, *P* < 0.001). This indicates that **weaker students
actually benefit more from the tutoring compared to stronger
ones**. The trend holds individually for the treatment groups of
the third year (*R* = -0.667, *P* < 0.005) and the fifth year
(*R* = -0.843, *P* < 0.001).

Although it is unlikely that ceiling effects influenced this, as
the highest overall score was 2 points below the maximum possible
24, the difference could be due to the fact that the mapping
between knowledge and score is not linear and it is harder to
improve a score that is already good. The difference from previous
literature might be due to difference in domains, instruments,
participants etc. and probably needs to be explored in future work.

#### 4.3.2. Effect of Engagement on Learning gains

*words_typed* and *learning_gains* were positively correlated
(*R* = 0.316, *P* = 0.009). The correlation is largely driven by
the 3rd year (*R* = 0.434, *P* = 0.007). This correlation is
stronger in the 3rd year treatment group (*R* = 0.454, *P* = 0.077)
than the 3rd year control group (*R* = 0.264, *P* = 0.275).
Similar trends are observed for the 5th year, although all
correlations are non-significant.

We further note that, overall, the *words_typed* is significantly
higher for the treatment group (*d* = 1.421, *P* < 0.001) and on
running an OLS Regression for *learning_gains* with respect to
condition, *words_typed* and year, we find that **the coefficient
for the treatment condition is non-significant**
(*coef* = -0.446, *P* = 0.666). This could mean that the benefit
of the treatment condition is **largely mediated by engagement**,
which is consistent with previous work (Altememy et al., 2023;
S. N. Jyothy and Achuthan, 2024).

#### 4.3.3. Hallucination and Other Errors

One major concern to deployment of GPT into educational scenarios
is the fact that it can give incorrect information, which can in
turn harm learning in students. To test the level of such errors,
students were asked every week if the tutor had made some errors
in their chats. Of **160 responses, only 16** indicated that there
was a problem. Only one of these was from year 5, about the
exercise being too long which is not a hallucination. Of the
remaining 15, 10 instances referred to single-point errors, i.e.,
at most 1 sentence had an issue. A further 2 responses complained
on the nature of the exercise, which is again not a hallucination.
Only 3 responses said that multiple sentences were wrong (3 of
which came from the same user).

We went over all the conversations from the given weeks, and found
a total of 4 errors:

- In one case the tutor suggested a change of verb, but then
  suggested not changing it when the student agreed.
- Another case where the correct answer was not in the options.
- One where the tutor rejected a correct answer that was different
  from what it expected.
- One where both options provided were correct depending on
  context.

Overall, this means that the tutor made no more than **14 errors
over 1,549 questions** (and never doubled down on its errors)
giving a hallucination rate of **less than 1%** which is well
within acceptable thresholds.

### 4.4. Novelty Effects

To investigate the novelty effects we look at whether students'
judgement of *comprehensiveness*, *level_of_resources*,
*usefulness*, and *interestingness* varies over the weeks. Since
the homeworks as well as weekly surveys are entirely voluntary,
not every student filled in the surveys for each week (the surveys
were designed to be instituted after finishing lessons according
to the original lesson plan, so despite the actual experiment
running for 8 weeks, we did only 6 surveys). The presence of a
novelty effect would be indicated by a drop in ratings over the
weeks.

The results of the tests show that for *interestingness*,
*level_of_resources*, and *comprehensiveness*, all the quartiles
overlap, with the means lying in the region of overlap.
*usefulness* seems to vary from week to week, but the pattern is
quite random, and no steady decline is visible. While this is not
sufficient to show a lack of novelty effect, we can still say that
**it is not strong enough to pose a threat to the validity of our
study**.

## 5. Conclusions and Discussion

In this work, we run an RCT to evaluate the ability of GPT-4 to
function as a tutor. We find that students find this replacement
of homework more useful and interesting, and are enthusiastic
about continuing using it in their education. In addition to this,
we also observe some improvement in learning as measured by tests.
Also, we do not find evidence of bias towards stronger students or
harmful hallucinations. We further notice that the self-assessments
don't show significant decline over the RCT period, thereby making
novelty effects less likely.

We do observe some issues with the tutor revealing answers too
much, especially when students try to game the system, but the
benefits seem to outweigh the drawbacks. **The learning gains are
also much smaller than the potential 2-sigma improvement, but this
can be attributed to the small time scale.** Further work in this
field could explore:

- Extension of the tutor to other languages and subjects.
- More directed prompts for specific types of exercises.
- Including aspects of student modelling and pedagogical
  strategies.
- More long-term effects of AI-based tutoring.

School and homework are often perceived as an unwelcome chore by
students, and according to the personal experience of some
teachers we worked with, there is an increasing lack of interest
and engagement from the students, making interventions on these
aspects even more needed. In addition, students more often felt
that they had the necessary resources to complete what was
required for them. Many parents cannot afford after-school services
and personal tutoring for their children, and struggling students
are often left lagging behind. Empowering a larger number of
students with the resources needed to achieve what is expected for
them has the potential to reduce the gap between students living
in more and less privileged circumstances, providing a fairer
playing field within schools. Given the continuing development of
LLMs to improve them across all tasks, we believe that our study
shows us the glimpse of a very bright future where hard-to-scale
tasks like tutoring can be taken over by AI tutors, bringing the
benefit of tutoring to a much greater number of students around
the world.

## 6. Ethics Statement

This study was approved by the Human Subjects Committee of the
Faculty of Economics, Business Administration, and Information
Technology of the University of Zurich (OEC IRB # 2024-018). All
participants provided informed consent prior to enrollment. For
minors, the consent was provided by both parents or legal tutors,
unless one parent or tutor alone had sole tutorship. Participant
confidentiality was strictly maintained, and all data were
anonymized. The study complied with all applicable regulations and
ethical standards. Each aspect of the design was discussed and
developed in collaboration with education professionals and with
the school personnel involved, to ensure an optimal and fair
experience for all participants and non-participants. The school
personnel was informed of the potential risk and instructed to
carefully monitor participants as well as non-participating
students potentially affected by the study, and to provide them
with extensive support.

## Acknowledgements

We extend our sincerest thanks to the teachers, staff, and
administration of Istituto Pindemonte in Verona for their support
in conducting this study, especially Dr. Lara Quarti, in whose
classes the experiment was conducted. We thank Dr. Julia Chatain
for her guidance on the framing of this study. We thank Shashank
Sonkar, Shehzaad Dhuliawala and Manuel Bernal-Lecina for their
feedback on the final drafts of the paper. Sankalan Pal Chowdhury
additionally thanks his colleagues Manuela Pineros-Rodriguez, Fan
Wang and Adrienn Toth for their helpful insights during
discussions about this project. He is partially funded by the
ETH-EPFL Joint Doctoral Program for Learning Sciences. This
project was funded by a grant from the Swiss National Science
Foundation (Project No. 197155) and a Responsible AI grant by the
Haslerstiftung.

## References

- Altememy, H. A., Neamah, N. R., Mazhair, R., Naser, N. S., Fahad,
  A. A., Al-Sammarraie, N. A., Sharif, H. R., Alseidi, M. A., &
  Al-Muttar, M. Y. O. (2023). AI Tools' Impact on Student
  Performance: Focusing on Student Motivation & Engagement in Iraq.
  *Przestrzeń Społeczna (Social Space)* 23(2), 143–165.
- Aruleba, K., Sanusi, I. T., Obaido, G., & Ogbuokiri, B. (2023).
  Integrating ChatGPT in a Computer Science Course: Students
  Perceptions and Suggestions. arXiv:2402.01640.
- Baidoo-Anu, D., & Ansah, L. O. (2023). Education in the era of
  generative artificial intelligence (AI): Understanding the
  potential benefits of ChatGPT in promoting teaching and learning.
  *Journal of AI* 7(1), 52–62.
- Bloom, B. S. (1984). The 2 Sigma Problem: The Search for Methods
  of Group Instruction as Effective as One-to-One Tutoring.
  *Educational Researcher* 13(6), 4–16.
- Butgereit, L., Martinus, H., & Abugosseisa, M. M. (2023). Prof Pi:
  Tutoring Mathematics in Arabic Language using GPT-4 and WhatsApp.
  In *2023 IEEE 27th International Conference on Intelligent
  Engineering Systems (INES)*.
- Cai, Z., Hu, X., & Graesser, A. C. (2019). Authoring Conversational
  Intelligent Tutoring Systems. In *Adaptive Instructional Systems*.
- Campani, G. (2013). Private Tutoring in Italy: Shadow Education
  in a Changing Context. Brill.
- Chelli, M. et al. (2024). Hallucination Rates and Reference
  Accuracy of ChatGPT and Bard for Systematic Reviews: Comparative
  Analysis. *Journal of Medical Internet Research* 26, e53164.
- Chen, C.-H. & Chang, C.-L. (2024). Effectiveness of AI-assisted
  game-based learning on science learning outcomes, intrinsic
  motivation, cognitive load, and learning behavior. *Education
  and Information Technologies*.
- Chheang, V. et al. (2024). Towards Anatomy Education with
  Generative AI-based Virtual Assistants in Immersive Virtual
  Reality Environments. arXiv:2306.17278.
- Choudhuri, R., Liu, D., Steinmacher, I., Gerosa, M., & Sarma, A.
  (2023). How Far Are We? The Triumphs and Trials of Generative AI
  in Learning Software Engineering. arXiv:2312.11719.
- Chowdhury, S. P., Zouhar, V., & Sachan, M. (2024). AutoTutor meets
  Large Language Models: A Language Model Tutor with Rich Pedagogy
  and Guardrails. ACM Conference on Learning @ Scale.
- Chu, J., Liu, Y., Yang, Z., Shen, X., Backes, M., & Zhang, Y.
  (2024). Comprehensive assessment of jailbreak attacks against
  llms. arXiv:2402.05668.
- Cipriano, B. P. & Alves, P. (2024). "ChatGPT Is Here to Help, Not
  to Replace Anybody"—An Evaluation of Students' Opinions On
  Integrating ChatGPT In CS Courses. arXiv:2404.17443.
- Cohen, P. A., Kulik, J. A., & Kulik, C.-L. C. (1982). Educational
  outcomes of tutoring: A meta-analysis of findings. *American
  Educational Research Journal* 19(2), 237–248.
- Dehouche, N. (2021). Plagiarism in the age of massive Generative
  Pre-trained Transformers (GPT-3). *Ethics in Science and
  Environmental Politics* 21, 17–23.
- Ferguson, R., & Sharples, M. (2014). Innovative Pedagogy at
  Massive Scale: Teaching and Learning in MOOCs. In *Open Learning
  and Teaching in Educational Communities*.
- Jacobs, S. & Jaschke, S. (2024). Evaluating the Application of
  Large Language Models to Generate Feedback in Programming
  Education. In *2024 IEEE Global Engineering Education Conference
  (EDUCON)*.
- Kasneci, E. et al. (2023). ChatGPT for good? On opportunities and
  challenges of large language models for education. *Learning and
  Individual Differences* 103, 102274.
- Kavadella, A. et al. (2024). Evaluation of ChatGPT's Real-Life
  Implementation in Undergraduate Dental Education: Mixed Methods
  Study. *JMIR Med Educ* 10, e51344.
- Kazemitabaar, M. et al. (2024). CodeAid: Evaluating a Classroom
  Deployment of an LLM-based Programming Assistant. *CHI '24*.
- Krupp, L. et al. (2023). Unreflected Acceptance—Investigating the
  Negative Consequences of ChatGPT-Assisted Problem Solving in
  Physics Education. arXiv:2309.03087.
- Li, K. & Keller, J. M. (2018). Use of the ARCS model in education:
  A literature review. *Computers & Education* 122, 54–62.
- Li, W., Pea, R., Haber, N., & Subramonyam, H. (2024). Tutorly:
  Turning Programming Videos Into Apprenticeship Learning
  Environments with LLMs. arXiv:2405.12946.
- Liffiton, M., Sheese, B., Savelka, J., & Denny, P. (2023).
  CodeHelp: Using Large Language Models with Guardrails for Scalable
  Support in Programming Classes. arXiv:2308.06921.
- Liu, R. et al. (2024). Teaching CS50 with AI: Leveraging
  Generative Artificial Intelligence in Computer Science Education.
  *SIGCSE 2024*.
- Lyu, W. et al. (2024). Evaluating the Effectiveness of LLMs in
  Introductory Computer Science Education: A Semester-Long Field
  Study. *L@S '24*.
- Nwana, H. S. (1990). Intelligent tutoring systems: an overview.
  *Artificial Intelligence Review* 4(4), 251–277.
- Odekeye, O. T. et al. (n.d.). Will AI Writing Tools Revolutionise
  Learning Attitudes—Insight from Undergraduate Students of Global
  South. SSRN 4755024.
- OpenAI & GPT-4 Team. (2024). GPT-4 Technical Report.
  arXiv:2303.08774.
- Padiyath, A. et al. (2024). Insights from Social Shaping Theory:
  The Appropriation of Large Language Models in an Undergraduate
  Programming Course. *ACM Conference on International Computing
  Education Research*.
- Pankiewicz, M. & Baker, R. S. (2024). Navigating Compiler Errors
  with AI Assistance—A Study of GPT Hints in an Introductory
  Programming Course. *ITiCSE 2024*.
- Pardos, Z. A. & Bhandari, S. (2024). ChatGPT-generated help
  produces learning gains equivalent to human tutor-authored help
  on mathematics skills. *PLOS ONE* 19(5), e0304013.
- Park, M., Kim, S., Lee, S., Kwon, S., & Kim, K. (2024).
  Empowering Personalized Learning through a Conversation-based
  Tutoring System with Student Modeling. *CHI '24 Extended
  Abstracts*.
- Polakova, P. & Klimova, B. (2024). Implementation of AI-driven
  technology into education—a pilot study on the use of chatbots in
  foreign language learning. *Cogent Education* 11(1), 2355385.
- Prather, J. et al. (2024). The Widening Gap: The Benefits and
  Harms of Generative AI for Novice Programmers. arXiv:2405.17739.
- Qi, L. et al. (2024). A Knowledge-Component-Based Methodology for
  Evaluating AI Assistants. arXiv:2406.05603.
- Ramdass, D. & Zimmerman, B. J. (2011). Developing self-regulation
  skills: The important role of homework. *Journal of Advanced
  Academics* 22(2), 194–218.
- S. N. Jyothy, R. R., Kolil, V. K., & Achuthan, K. (2024).
  Exploring large language models as an integrated tool for
  learning, teaching, and research through the Fogg Behavior Model.
  *Cogent Engineering* 11(1), 2353494.
- Schartel, S. A. (2012). Giving feedback—An integral part of
  education. *Best Practice & Research Clinical Anaesthesiology*
  26(1), 77–87.
- Schmucker, R., Xia, M., Azaria, A., & Mitchell, T. (2024).
  Ruffle&Riley: Insights from Designing and Evaluating a Large
  Language Model-Based Conversational Tutoring System.
  arXiv:2404.17460.
- Tanay, B. A., Arinze, L., Joshi, S. S., Davis, K. A., & Davis,
  J. C. (2024). An Exploratory Study on Upper-Level Computing
  Students' Use of Large Language Models as Tools in a
  Semester-Long Project. arXiv:2403.18679.
- Team, Gemini. (2024). Gemini: A Family of Highly Capable
  Multimodal Models. arXiv:2312.11805.
- Thway, M., Recatala-Gomez, J., Lim, F. S., Hippalgaonkar, K., &
  Ng, L. W. T. (2024). Battling Botpoop using GenAI for Higher
  Education. arXiv:2406.07796.
- Touvron, H. et al. (2023). LLaMA: Open and Efficient Foundation
  Language Models. arXiv:2302.13971.
- Tuan, H.-L., Chin, C.-C., & Shieh, S.-H. (2005). The development
  of a questionnaire to measure students' motivation towards
  science learning. *International Journal of Science Education*
  27(6), 639–654.
- Wang, R. et al. (2024). PATIENT-Ψ: Using Large Language Models to
  Simulate Patients for Training Mental Health Professionals.
  arXiv:2405.19660.
- Yang, B. et al. (2024). CREF: An LLM-based Conversational
  Software Repair Framework for Programming Tutors.
  arXiv:2406.13972.
- Zhai, C., Wibowo, S., & Li, L. D. (2024). The effects of
  over-reliance on AI dialogue systems on students' cognitive
  abilities: a systematic review. *Smart Learning Environments*
  11(1), 28.
- Zhang, J. et al. (2024). Investigation of the effectiveness of
  applying ChatGPT in Dialogic Teaching Using
  Electroencephalography. arXiv:2403.16687.

## Appendix B. Prompts (excerpts)

### B.1. Tutoring Prompt

The following prompt was the main prompt given to the tutor as the
system prompt. The placeholders are replaced with assignment
purpose, description and example from the teacher. Note that the
Common European Framework of Reference for Languages was mistakenly
referred to as "Cambridge Framework" during the execution of the
study.

> We are helping students learn English as a second language. We
> give you an exercise as a starting point. Act as a tutor and
> drive the student through the same concepts, testing the
> understanding step by step. It is not necessary to replicate the
> example exercise, as long as you cover the same concepts. Follow
> the tutoring strategy we provide. Start with a brief explanation
> of the concept. Provide at least 10 questions, one by one. Do
> not move on until the student gives the correct answer. If
> necessary, provide explanations and feedback. **Never give the
> answer to the question.** Do not give the answer to the question
> as a part of the explanation. Point out all grammar and spelling
> mistakes. Keep a B2 level of English according to the Cambridge
> framework. Once all questions are solved, ask the student if
> they wish to practice more. If they don't, output `EXERCISE
> PURPOSE: +++ purpose +++ EXERCISE DESCRIPTION +++ description
> +++ EXERCISE EXAMPLE (NOT VISIBLE TO THE STUDENT) +++ example
> +++ TUTORING STRATEGY +++ strategy +++`.

### B.2. Strategy Generation Prompt

> We are helping students learn English as a second language. We
> give you an exercise as a starting point. Provide a concise,
> step-by-step strategy for a short dialog-based tutoring session
> led by ChatGPT with a student covering the same concepts. The
> tutoring session is text-based and led through a chat interface.
> Describe the strategy with a maximum of six sentences. Keep a B2
> level of English according to the Cambridge framework.
> `+++ assignment.purpose +++ +++ assignment.description +++ +++
> assignment.example +++`.

## Appendix A.1. Regression Tables

**Table 7. OLS Regression Results: Learning Gains Mediated by
Student Engagement**

| Variable      | Coefficient | Std. Error |
| ------------- | ----------- | ---------- |
| Intercept     | 3.5828      | 0.743      |
| Treatment     | -0.4456     | 1.027      |
| 3rd Year      | 4.0815      | 0.852      |
| Words Typed   | 0.001       | 0.001      |
