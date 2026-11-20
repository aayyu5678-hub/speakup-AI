# SpeakUp AI - Expanded Listening Comprehension Scenarios
# Rich, realistic dialogues across Formal, Informal, Professional, and Friendly categories.

LISTENING_DIALOGUES = [
    # ==========================================
    # 1. FORMAL CONVERSATIONS
    # ==========================================
    {
        "id": 1,
        "key": "formal_teacher",
        "title": "Speaking with a Professor: Requesting an Extension",
        "category": "Formal",
        "category_slug": "formal",
        "difficulty": "Intermediate",
        "duration": "~55 sec",
        "situation": "A computer science student visits Professor Miller's office hours to discuss lab benchmark results and politely request a two-day extension due to server maintenance.",
        "audio_text": "Good afternoon, Professor Miller. Do you have a quick moment? Of course, Rahul. Come in and take a seat. How is your database project progressing? It is going well, Professor, but our team hit an unexpected roadblock yesterday. The university server underwent unscheduled maintenance, which delayed our query performance benchmarks. Understood. Technical setbacks happen in real-world systems. How much additional time do you realistically require? If possible, a forty-eight hour extension until Thursday evening would allow us to finalize testing and submit a thorough report. That seems reasonable, Rahul. Submit the report by Thursday at six PM, and make sure to document the server latency in your appendix. Thank you so much, Professor Miller. I appreciate your guidance.",
        "dialogue": [
            {"speaker": "Rahul (Student)", "text": "Good afternoon, Professor Miller. Do you have a quick moment?"},
            {"speaker": "Professor Miller", "text": "Of course, Rahul. Come in and take a seat. How is your database project progressing?"},
            {"speaker": "Rahul (Student)", "text": "It is going well, Professor, but our team hit an unexpected roadblock yesterday. The university server underwent unscheduled maintenance, which delayed our query performance benchmarks."},
            {"speaker": "Professor Miller", "text": "Understood. Technical setbacks happen in real-world systems. How much additional time do you realistically require?"},
            {"speaker": "Rahul (Student)", "text": "If possible, a forty-eight hour extension until Thursday evening would allow us to finalize testing and submit a thorough report."},
            {"speaker": "Professor Miller", "text": "That seems reasonable, Rahul. Submit the report by Thursday at six PM, and make sure to document the server latency in your appendix."},
            {"speaker": "Rahul (Student)", "text": "Thank you so much, Professor Miller. I appreciate your guidance."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "What unexpected obstacle caused the project delay?",
                "options": [
                    {"val": "a", "text": "The student was sick and missed laboratory classes"},
                    {"val": "b", "text": "Unscheduled university server maintenance delayed benchmarks"},
                    {"val": "c", "text": "The team forgot to implement database indexing"}
                ],
                "correct": "b",
                "explanation": "Rahul explains that unscheduled maintenance on the university server delayed their query benchmark experiments."
            },
            {
                "q_id": 2,
                "question": "What condition did Professor Miller set when granting the Thursday 6 PM deadline?",
                "options": [
                    {"val": "a", "text": "Document the server latency in the report appendix"},
                    {"val": "b", "text": "Work with a different team partner"},
                    {"val": "c", "text": "Present the project in front of the entire class"}
                ],
                "correct": "a",
                "explanation": "Professor Miller asked Rahul to be sure to document the server latency in the appendix of the report."
            }
        ]
    },
    {
        "id": 2,
        "key": "formal_office",
        "title": "Asking for Information at an Office: Registrar Verification",
        "category": "Formal",
        "category_slug": "formal",
        "difficulty": "Beginner",
        "duration": "~45 sec",
        "situation": "A student visits the University Registrar counter to request an official academic transcript and verify the processing fee and dispatch timeline.",
        "audio_text": "Good morning. How may I assist you today? Hello. I need an official sealed transcript for my upcoming campus placement background check. Certainly. Have you already submitted the online verification form on the student portal? Yes, I submitted it yesterday and received a confirmation reference number. Perfect. Standard processing takes three working days, or you can opt for expedited counter delivery by three PM tomorrow for an additional fee of ten dollars. Tomorrow afternoon would be ideal, as my interview is on Friday morning. Great. Please sign this verification voucher, and remember to bring your student ID card when collecting the document tomorrow.",
        "dialogue": [
            {"speaker": "Registrar Officer", "text": "Good morning. How may I assist you today?"},
            {"speaker": "Student", "text": "Hello. I need an official sealed transcript for my upcoming campus placement background check."},
            {"speaker": "Registrar Officer", "text": "Certainly. Have you already submitted the online verification form on the student portal?"},
            {"speaker": "Student", "text": "Yes, I submitted it yesterday and received a confirmation reference number."},
            {"speaker": "Registrar Officer", "text": "Perfect. Standard processing takes three working days, or you can opt for expedited counter delivery by three PM tomorrow for an additional fee of ten dollars."},
            {"speaker": "Student", "text": "Tomorrow afternoon would be ideal, as my interview is on Friday morning."},
            {"speaker": "Registrar Officer", "text": "Great. Please sign this verification voucher, and remember to bring your student ID card when collecting the document tomorrow."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "Why does the student need an expedited official transcript?",
                "options": [
                    {"val": "a", "text": "To apply for an overseas tourist visa"},
                    {"val": "b", "text": "For a campus placement interview verification on Friday"},
                    {"val": "c", "text": "To transfer to another university immediately"}
                ],
                "correct": "b",
                "explanation": "The student states that the transcript is needed for a placement verification and their interview is on Friday morning."
            },
            {
                "q_id": 2,
                "question": "What must the student bring when collecting the transcript tomorrow?",
                "options": [
                    {"val": "a", "text": "A letter from their department head"},
                    {"val": "b", "text": "Their university student ID card"},
                    {"val": "c", "text": "Their original high school diploma"}
                ],
                "correct": "b",
                "explanation": "The officer tells the student to remember to bring their student ID card when picking up the document."
            }
        ]
    },
    {
        "id": 3,
        "key": "formal_appointment",
        "title": "Making Appointments: Academic Advisory Consultation",
        "category": "Formal",
        "category_slug": "formal",
        "difficulty": "Beginner",
        "duration": "~50 sec",
        "situation": "A student calls the Dean's Academic Advisory desk to book a thirty-minute consultation regarding elective course credits and internship prerequisites.",
        "audio_text": "Academic Advisory Services, good morning. Hello, my name is Ananya. I would like to schedule an appointment with Dr. Henderson to discuss my semester elective credits. Certainly, Ananya. Dr. Henderson has availability on Tuesday at ten AM or Wednesday at two thirty PM. Would either of those suit your class schedule? Wednesday afternoon at two thirty PM works perfectly, since I have a lab lecture on Tuesday mornings. Excellent. I have reserved Wednesday at two thirty PM for you. Please arrive five minutes early and bring an updated copy of your degree audit sheet. Thank you very much for your help. Have a wonderful day.",
        "dialogue": [
            {"speaker": "Desk Assistant", "text": "Academic Advisory Services, good morning."},
            {"speaker": "Ananya (Student)", "text": "Hello, my name is Ananya. I would like to schedule an appointment with Dr. Henderson to discuss my semester elective credits."},
            {"speaker": "Desk Assistant", "text": "Certainly, Ananya. Dr. Henderson has availability on Tuesday at ten AM or Wednesday at two thirty PM. Would either of those suit your class schedule?"},
            {"speaker": "Ananya (Student)", "text": "Wednesday afternoon at two thirty PM works perfectly, since I have a lab lecture on Tuesday mornings."},
            {"speaker": "Desk Assistant", "text": "Excellent. I have reserved Wednesday at two thirty PM for you. Please arrive five minutes early and bring an updated copy of your degree audit sheet."},
            {"speaker": "Ananya (Student)", "text": "Thank you very much for your help. Have a wonderful day."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "Why did Ananya decline the Tuesday morning appointment slot?",
                "options": [
                    {"val": "a", "text": "She has an active lab lecture on Tuesday morning"},
                    {"val": "b", "text": "She was traveling out of town"},
                    {"val": "c", "text": "The advisor was already fully booked"}
                ],
                "correct": "a",
                "explanation": "Ananya explained that she has a lab lecture on Tuesday mornings, making Wednesday at 2:30 PM the ideal time."
            },
            {
                "q_id": 2,
                "question": "What document should Ananya bring to the advisory session?",
                "options": [
                    {"val": "a", "text": "A printed degree audit sheet"},
                    {"val": "b", "text": "A recommendation letter from her employer"},
                    {"val": "c", "text": "A handwritten permission slip"}
                ],
                "correct": "a",
                "explanation": "The assistant asked her to bring an updated copy of her degree audit sheet."
            }
        ]
    },
    {
        "id": 4,
        "key": "formal_academic",
        "title": "Discussing Academic Matters: Thesis Methodology Review",
        "category": "Formal",
        "category_slug": "formal",
        "difficulty": "Advanced",
        "duration": "~65 sec",
        "situation": "A graduate researcher reviews their experimental sampling methodology, sample size significance, and quantitative metrics with their thesis supervisor.",
        "audio_text": "Good morning, Dr. Rao. I have compiled the preliminary quantitative metrics from our algorithm evaluation. Excellent, Priya. Did your cross-validation results demonstrate statistical significance across diverse dataset distributions? Yes, Dr. Rao. We applied a ten-fold cross-validation across three synthetic benchmark suites and two real-world telemetry traces. The latency variance dropped by twelve percent compared to baseline heuristics. That is promising, but how did you control for transient network jitter during the real-world traces? We recorded network packet loss and ping variance concurrently, applying a Kalman filter to eliminate transient anomalies from the training dataset. Very thorough methodology. Be sure to articulate that filtering rationale clearly in your methodology chapter so the peer reviewers appreciate your rigor.",
        "dialogue": [
            {"speaker": "Priya (Researcher)", "text": "Good morning, Dr. Rao. I have compiled the preliminary quantitative metrics from our algorithm evaluation."},
            {"speaker": "Dr. Rao (Supervisor)", "text": "Excellent, Priya. Did your cross-validation results demonstrate statistical significance across diverse dataset distributions?"},
            {"speaker": "Priya (Researcher)", "text": "Yes, Dr. Rao. We applied a ten-fold cross-validation across three synthetic benchmark suites and two real-world telemetry traces. The latency variance dropped by twelve percent compared to baseline heuristics."},
            {"speaker": "Dr. Rao (Supervisor)", "text": "That is promising, but how did you control for transient network jitter during the real-world traces?"},
            {"speaker": "Priya (Researcher)", "text": "We recorded network packet loss and ping variance concurrently, applying a Kalman filter to eliminate transient anomalies from the training dataset."},
            {"speaker": "Dr. Rao (Supervisor)", "text": "Very thorough methodology. Be sure to articulate that filtering rationale clearly in your methodology chapter so the peer reviewers appreciate your rigor."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "What was the quantitative improvement achieved by Priya's algorithm?",
                "options": [
                    {"val": "a", "text": "A twelve percent reduction in latency variance"},
                    {"val": "b", "text": "A fifty percent reduction in memory consumption"},
                    {"val": "c", "text": "A doubling of server hardware costs"}
                ],
                "correct": "a",
                "explanation": "Priya reported that the latency variance dropped by twelve percent compared to baseline heuristics."
            },
            {
                "q_id": 2,
                "question": "How did the researcher handle transient network jitter in the empirical traces?",
                "options": [
                    {"val": "a", "text": "By discarding all real-world data entirely"},
                    {"val": "b", "text": "By applying a Kalman filter to recorded packet loss and ping variance"},
                    {"val": "c", "text": "By manually estimating the missing values"}
                ],
                "correct": "b",
                "explanation": "Priya explained they applied a Kalman filter to packet loss and ping variance to eliminate transient anomalies."
            }
        ]
    },

    # ==========================================
    # 2. INFORMAL CONVERSATIONS
    # ==========================================
    {
        "id": 5,
        "key": "informal_friends",
        "title": "Talking with Friends: Planning a Weekend Hike",
        "category": "Informal",
        "category_slug": "informal",
        "difficulty": "Beginner",
        "duration": "~45 sec",
        "situation": "Two college friends, Leo and Maya, catch up over tea in the student union to plan a Saturday mountain trail hike.",
        "audio_text": "Hey Maya! Are we still on for hiking up Sunset Ridge this Saturday? Definitely! The weather forecast says clear blue skies and around twenty degrees Celsius. That sounds perfect. What time should we set off? If we leave by seven AM, we can reach the peak before noon and avoid the midday heat. Good thinking. I can borrow my brother's car and pick you up around six forty-five. Awesome! I will pack trail mix, fruit snacks, and plenty of water for both of us.",
        "dialogue": [
            {"speaker": "Leo", "text": "Hey Maya! Are we still on for hiking up Sunset Ridge this Saturday?"},
            {"speaker": "Maya", "text": "Definitely! The weather forecast says clear blue skies and around twenty degrees Celsius."},
            {"speaker": "Leo", "text": "That sounds perfect. What time should we set off?"},
            {"speaker": "Maya", "text": "If we leave by seven AM, we can reach the peak before noon and avoid the midday heat."},
            {"speaker": "Leo", "text": "Good thinking. I can borrow my brother's car and pick you up around six forty-five."},
            {"speaker": "Maya", "text": "Awesome! I will pack trail mix, fruit snacks, and plenty of water for both of us."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "Why does Maya suggest starting the hike early at 7:00 AM?",
                "options": [
                    {"val": "a", "text": "To reach the summit before noon and avoid the midday sun"},
                    {"val": "b", "text": "Because the park gates close at 10 AM"},
                    {"val": "c", "text": "To catch an early morning train back to city"}
                ],
                "correct": "a",
                "explanation": "Maya notes that leaving by 7 AM allows them to reach the peak before noon to beat the midday heat."
            },
            {
                "q_id": 2,
                "question": "What responsibility does Leo take for the trip?",
                "options": [
                    {"val": "a", "text": "Borrowing his brother's car to drive and pick Maya up"},
                    {"val": "b", "text": "Buying all the hiking boots and tents"},
                    {"val": "c", "text": "Hiring a professional mountain guide"}
                ],
                "correct": "a",
                "explanation": "Leo mentions that he can borrow his brother's car and pick Maya up at 6:45 AM."
            }
        ]
    },
    {
        "id": 6,
        "key": "informal_family",
        "title": "Daily Conversations with Family: Evening Catch-Up Call",
        "category": "Informal",
        "category_slug": "informal",
        "difficulty": "Beginner",
        "duration": "~45 sec",
        "situation": "A university student living in campus accommodation calls their mother to catch up on daily life, exams, and home-cooked dinner memories.",
        "audio_text": "Hi Mom! How are you doing back home? Hi sweetie! Everything is peaceful here. How was your day at college? Busy but really rewarding! I completed my software presentation today, and our professor praised our clean design. That is wonderful news, Rohan! I knew your hard work would pay off. Have you eaten dinner yet? Not yet, I am about to cook some pasta and steamed veggies. Remember to eat properly and get some good sleep tonight. I will, Mom. Give Dad my love, and I will call you again on Sunday!",
        "dialogue": [
            {"speaker": "Rohan", "text": "Hi Mom! How are you doing back home?"},
            {"speaker": "Mom", "text": "Hi sweetie! Everything is peaceful here. How was your day at college?"},
            {"speaker": "Rohan", "text": "Busy but really rewarding! I completed my software presentation today, and our professor praised our clean design."},
            {"speaker": "Mom", "text": "That is wonderful news, Rohan! I knew your hard work would pay off. Have you eaten dinner yet?"},
            {"speaker": "Rohan", "text": "Not yet, I am about to cook some pasta and steamed veggies."},
            {"speaker": "Mom", "text": "Remember to eat properly and get some good sleep tonight."},
            {"speaker": "Rohan", "text": "I will, Mom. Give Dad my love, and I will call you again on Sunday!"}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "What positive accomplishment did Rohan share with his mother?",
                "options": [
                    {"val": "a", "text": "His professor praised his software presentation's design"},
                    {"val": "b", "text": "He won a sports championship match"},
                    {"val": "c", "text": "He moved into a brand new apartment"}
                ],
                "correct": "a",
                "explanation": "Rohan shared that he completed his software presentation and the professor praised their clean design."
            },
            {
                "q_id": 2,
                "question": "What is Rohan planning to cook for his evening dinner?",
                "options": [
                    {"val": "a", "text": "Pasta and steamed vegetables"},
                    {"val": "b", "text": "Takeout pizza with friends"},
                    {"val": "c", "text": "Traditional lentil curry and rice"}
                ],
                "correct": "a",
                "explanation": "Rohan states that he is about to cook some pasta and steamed veggies."
            }
        ]
    },
    {
        "id": 7,
        "key": "informal_hobbies",
        "title": "Discussing Hobbies and Weekend Plans: Photography Workshop",
        "category": "Informal",
        "category_slug": "informal",
        "difficulty": "Intermediate",
        "duration": "~50 sec",
        "situation": "Two photography enthusiasts discuss camera settings, landscape lighting, and an upcoming weekend portrait editing masterclass.",
        "audio_text": "Hey Karan, I noticed your photos from the botanic gardens on Instagram. The macro depth of field was stunning! Thanks, Samira! I was experimenting with a fifty-millimeter prime lens with a wide aperture of f one point eight. It creates such smooth background blur. Exactly. Are you planning to attend the city digital arts workshop this Sunday? Yes, they have a two-hour practical session on RAW color grading and shadow balance. I am really eager to learn how to recover details in high-contrast golden hour shots. Me too! Let us register together so we can sit at the same editing workbench.",
        "dialogue": [
            {"speaker": "Samira", "text": "Hey Karan, I noticed your photos from the botanic gardens on Instagram. The macro depth of field was stunning!"},
            {"speaker": "Karan", "text": "Thanks, Samira! I was experimenting with a fifty-millimeter prime lens with a wide aperture of f one point eight. It creates such smooth background blur."},
            {"speaker": "Samira", "text": "Exactly. Are you planning to attend the city digital arts workshop this Sunday?"},
            {"speaker": "Karan", "text": "Yes, they have a two-hour practical session on RAW color grading and shadow balance. I am really eager to learn how to recover details in high-contrast golden hour shots."},
            {"speaker": "Samira", "text": "Me too! Let us register together so we can sit at the same editing workbench."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "What camera lens technique did Karan use for his botanical garden photos?",
                "options": [
                    {"val": "a", "text": "A 50mm prime lens with wide f/1.8 aperture for smooth background blur"},
                    {"val": "b", "text": "A telephoto zoom lens with harsh flash"},
                    {"val": "c", "text": "A smartphone panorama filter"}
                ],
                "correct": "a",
                "explanation": "Karan explained he used a 50mm prime lens at f/1.8 to create smooth background blur."
            },
            {
                "q_id": 2,
                "question": "What key skill is Karan hoping to practice at Sunday's workshop?",
                "options": [
                    {"val": "a", "text": "RAW color grading and recovering shadow details in high-contrast lighting"},
                    {"val": "b", "text": "Cleaning camera sensor dust"},
                    {"val": "c", "text": "Selling prints at an art auction"}
                ],
                "correct": "a",
                "explanation": "Karan states he is eager to learn RAW color grading and recovering shadow details in high-contrast golden hour shots."
            }
        ]
    },
    {
        "id": 8,
        "key": "informal_meeting",
        "title": "Meeting Someone New: First Day in the Tech Lab",
        "category": "Informal",
        "category_slug": "informal",
        "difficulty": "Intermediate",
        "duration": "~50 sec",
        "situation": "Two engineering students introduce themselves on the first day of their advanced algorithms laboratory and find common technical interests.",
        "audio_text": "Hi there! Mind if I take this workstation next to you? Not at all! Please go ahead. I am Dev, by the way. Nice to meet you, Dev! I am Nina. Are you in the third-year software engineering stream too? Yes, exactly. I am focusing on distributed backend systems and Python APIs. How about you? I am leaning toward machine learning and intelligent user interfaces. Have you worked with our lab instructor, Dr. Collins, before? Yes, I took her operating systems course last year. She is very approachable and expects practical, well-tested code. That is reassuring to hear! Maybe we could team up for the multi-threaded programming assignments.",
        "dialogue": [
            {"speaker": "Nina", "text": "Hi there! Mind if I take this workstation next to you?"},
            {"speaker": "Dev", "text": "Not at all! Please go ahead. I am Dev, by the way."},
            {"speaker": "Nina", "text": "Nice to meet you, Dev! I am Nina. Are you in the third-year software engineering stream too?"},
            {"speaker": "Dev", "text": "Yes, exactly. I am focusing on distributed backend systems and Python APIs. How about you?"},
            {"speaker": "Nina", "text": "I am leaning toward machine learning and intelligent user interfaces. Have you worked with our lab instructor, Dr. Collins, before?"},
            {"speaker": "Dev", "text": "Yes, I took her operating systems course last year. She is very approachable and expects practical, well-tested code."},
            {"speaker": "Nina", "text": "That is reassuring to hear! Maybe we could team up for the multi-threaded programming assignments."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "What technical domain is Nina primarily focusing on?",
                "options": [
                    {"val": "a", "text": "Machine learning and intelligent user interfaces"},
                    {"val": "b", "text": "Computer hardware micro-soldering"},
                    {"val": "c", "text": "Cybersecurity compliance auditing"}
                ],
                "correct": "a",
                "explanation": "Nina states that she is leaning toward machine learning and intelligent user interfaces."
            },
            {
                "q_id": 2,
                "question": "What insight does Dev share regarding instructor Dr. Collins?",
                "options": [
                    {"val": "a", "text": "She is approachable and places strong value on practical, well-tested code"},
                    {"val": "b", "text": "She only grades theoretical essay questions"},
                    {"val": "c", "text": "She recently joined the university this week"}
                ],
                "correct": "a",
                "explanation": "Dev shares that Dr. Collins is very approachable and expects practical, well-tested code."
            }
        ]
    },

    # ==========================================
    # 3. PROFESSIONAL CONVERSATIONS
    # ==========================================
    {
        "id": 9,
        "key": "prof_interview",
        "title": "Job Interviews: STAR Method on Technical Deadlines",
        "category": "Professional",
        "category_slug": "professional",
        "difficulty": "Advanced",
        "duration": "~65 sec",
        "situation": "A campus placement candidate answers a behavioral interview question about resolving a high-stakes engineering bottleneck under pressure.",
        "audio_text": "Welcome, Tanvi. Could you describe a situation where you encountered a critical technical bottleneck under a tight deadline, and how you resolved it? Certainly. During our final year web project, three days before our demonstration milestone, our database query response time spiked to four seconds under multi-user load. As team lead, I identified the task: we needed sub-second response times without rebuilding our database schema. For action, I profiled our database queries, identified missing compound indexes on user lookup tables, and implemented an in-memory caching layer for frequently accessed items. As a result, our latency dropped from four seconds to under eighty milliseconds, and our platform handled fifty concurrent mock users smoothly during the live evaluation. That is an excellent demonstration of root cause analysis and decisive action under pressure.",
        "dialogue": [
            {"speaker": "Interviewer", "text": "Welcome, Tanvi. Could you describe a situation where you encountered a critical technical bottleneck under a tight deadline, and how you resolved it?"},
            {"speaker": "Tanvi (Candidate)", "text": "Certainly. During our final year web project, three days before our demonstration milestone, our database query response time spiked to four seconds under multi-user load."},
            {"speaker": "Tanvi (Candidate)", "text": "As team lead, I identified the task: we needed sub-second response times without rebuilding our database schema."},
            {"speaker": "Tanvi (Candidate)", "text": "For action, I profiled our database queries, identified missing compound indexes on user lookup tables, and implemented an in-memory caching layer for frequently accessed items."},
            {"speaker": "Tanvi (Candidate)", "text": "As a result, our latency dropped from four seconds to under eighty milliseconds, and our platform handled fifty concurrent mock users smoothly during the live evaluation."},
            {"speaker": "Interviewer", "text": "That is an excellent demonstration of root cause analysis and decisive action under pressure."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "What concrete technical actions did Tanvi take to resolve the database bottleneck?",
                "options": [
                    {"val": "a", "text": "Profiled queries, added compound indexes, and implemented in-memory caching"},
                    {"val": "b", "text": "Bought new server hardware and deleted old user accounts"},
                    {"val": "c", "text": "Switched programming languages overnight"}
                ],
                "correct": "a",
                "explanation": "Tanvi explains that she profiled queries, identified missing compound indexes, and added an in-memory caching layer."
            },
            {
                "q_id": 2,
                "question": "What was the final outcome achieved before the demo?",
                "options": [
                    {"val": "a", "text": "Latency dropped from four seconds to under eighty milliseconds"},
                    {"val": "b", "text": "The presentation had to be postponed by two weeks"},
                    {"val": "c", "text": "The database crashed during the live test"}
                ],
                "correct": "a",
                "explanation": "Tanvi stated that response time fell from 4 seconds to under 80 milliseconds, handling 50 concurrent users smoothly."
            }
        ]
    },
    {
        "id": 10,
        "key": "prof_meeting",
        "title": "Workplace Meetings: Sprint Retrospective & Backlog Refinement",
        "category": "Professional",
        "category_slug": "professional",
        "difficulty": "Intermediate",
        "duration": "~55 sec",
        "situation": "A cross-functional software product team reviews last sprint's velocity, user story estimations, and deployment pipeline improvements.",
        "audio_text": "Good morning team. Let us review our sprint velocity before refining the upcoming backlog. Overall, we completed forty-two story points out of forty-eight planned. What caused the six-point spillover on the payment gateway integration? We ran into ambiguous webhook specifications from the payment vendor, which required two days of asynchronous email clarification. Fair enough. For the next sprint, let us add a preliminary API contract review during backlog grooming so technical spikes happen before sprint commitment. Agreed. That will prevent engineers from getting blocked during active sprint implementation.",
        "dialogue": [
            {"speaker": "Scrum Master", "text": "Good morning team. Let us review our sprint velocity before refining the upcoming backlog. Overall, we completed forty-two story points out of forty-eight planned."},
            {"speaker": "Scrum Master", "text": "What caused the six-point spillover on the payment gateway integration?"},
            {"speaker": "Developer (Alex)", "text": "We ran into ambiguous webhook specifications from the payment vendor, which required two days of asynchronous email clarification."},
            {"speaker": "Scrum Master", "text": "Fair enough. For the next sprint, let us add a preliminary API contract review during backlog grooming so technical spikes happen before sprint commitment."},
            {"speaker": "Developer (Alex)", "text": "Agreed. That will prevent engineers from getting blocked during active sprint implementation."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "What caused the six-point story spillover in the sprint?",
                "options": [
                    {"val": "a", "text": "Ambiguous third-party webhook specs requiring vendor clarification"},
                    {"val": "b", "text": "A total power outage in the office"},
                    {"val": "c", "text": "The team forgot to write unit tests"}
                ],
                "correct": "a",
                "explanation": "Alex explained that ambiguous webhook specifications from the payment vendor required two days of clarification."
            },
            {
                "q_id": 2,
                "question": "What preventive process change did the team agree to adopt?",
                "options": [
                    {"val": "a", "text": "Conducting API contract reviews during backlog grooming prior to commitment"},
                    {"val": "b", "text": "Working over weekends to double velocity"},
                    {"val": "c", "text": "Eliminating all third-party integrations"}
                ],
                "correct": "a",
                "explanation": "The Scrum Master suggested preliminary API contract reviews during backlog grooming so spikes happen before commitment."
            }
        ]
    },
    {
        "id": 11,
        "key": "prof_colleagues",
        "title": "Communicating with Colleagues: API Contract Alignment",
        "category": "Professional",
        "category_slug": "professional",
        "difficulty": "Intermediate",
        "duration": "~50 sec",
        "situation": "A frontend UI developer and a backend engineer coordinate on REST API response format, HTTP error status codes, and authorization headers.",
        "audio_text": "Hey Marcus, do you have five minutes to align on the user profile endpoint? Sure, Chloe. What is on your mind? On the frontend, when a user updates their password, we are expecting a JSON payload with a success boolean and a message string. Currently, the endpoint returns raw text on error. Good catch. I will standardize the response so that validation errors return HTTP four hundred with a structured JSON object containing an error message. That would make error handling much cleaner on our side! Also, please make sure the authorization bearer token is verified before parsing the request body. Absolutely, Chloe. I will update the pull request within thirty minutes.",
        "dialogue": [
            {"speaker": "Chloe (Frontend)", "text": "Hey Marcus, do you have five minutes to align on the user profile endpoint?"},
            {"speaker": "Marcus (Backend)", "text": "Sure, Chloe. What is on your mind?"},
            {"speaker": "Chloe (Frontend)", "text": "On the frontend, when a user updates their password, we are expecting a JSON payload with a success boolean and a message string. Currently, the endpoint returns raw text on error."},
            {"speaker": "Marcus (Backend)", "text": "Good catch. I will standardize the response so that validation errors return HTTP four hundred with a structured JSON object containing an error message."},
            {"speaker": "Chloe (Frontend)", "text": "That would make error handling much cleaner on our side! Also, please make sure the authorization bearer token is verified before parsing the request body."},
            {"speaker": "Marcus (Backend)", "text": "Absolutely, Chloe. I will update the pull request within thirty minutes."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "What inconsistency did Chloe point out in the backend endpoint?",
                "options": [
                    {"val": "a", "text": "The endpoint was returning raw text on error rather than structured JSON"},
                    {"val": "b", "text": "The server was completely offline"},
                    {"val": "c", "text": "Passwords were being displayed in plain text"}
                ],
                "correct": "a",
                "explanation": "Chloe pointed out that on error, the endpoint returned raw text instead of structured JSON with a success flag and message."
            },
            {
                "q_id": 2,
                "question": "What HTTP status code will Marcus return for validation errors?",
                "options": [
                    {"val": "a", "text": "HTTP 400 (Bad Request)"},
                    {"val": "b", "text": "HTTP 200 (OK)"},
                    {"val": "c", "text": "HTTP 500 (Internal Server Error)"}
                ],
                "correct": "a",
                "explanation": "Marcus agreed to return HTTP 400 with a structured JSON error object for validation failures."
            }
        ]
    },
    {
        "id": 12,
        "key": "prof_presentation",
        "title": "Giving Presentations: Product Pitch & Stakeholder Q&A",
        "category": "Professional",
        "category_slug": "professional",
        "difficulty": "Advanced",
        "duration": "~65 sec",
        "situation": "A technical lead pitches an intelligent speech-to-speech coaching application to university executives and addresses enterprise privacy concerns.",
        "audio_text": "Good afternoon, distinguished committee members. Traditional language labs provide static audio, but they fail to build spontaneous spoken confidence. SpeakUp AI solves this by coupling low-latency language models with dynamic pronunciation feedback, allowing students to rehearse real-world dialogues anytime. Thank you for that compelling overview, Vikram. Can you explain how student voice recordings are handled to guarantee compliance with university data privacy regulations? Certainly, Provost Campbell. Audio streams are processed strictly in ephemeral memory for phoneme analysis. No raw biometric voice data is stored on external cloud storage without student consent, and all database records are encrypted at rest with zero data retention for third-party model training. That address our compliance mandate directly. Please proceed with the pilot deployment timeline.",
        "dialogue": [
            {"speaker": "Vikram (Presenter)", "text": "Good afternoon, distinguished committee members. Traditional language labs provide static audio, but they fail to build spontaneous spoken confidence. SpeakUp AI solves this by coupling low-latency language models with dynamic pronunciation feedback, allowing students to rehearse real-world dialogues anytime."},
            {"speaker": "Provost Campbell", "text": "Thank you for that compelling overview, Vikram. Can you explain how student voice recordings are handled to guarantee compliance with university data privacy regulations?"},
            {"speaker": "Vikram (Presenter)", "text": "Certainly, Provost Campbell. Audio streams are processed strictly in ephemeral memory for phoneme analysis. No raw biometric voice data is stored on external cloud storage without student consent, and all database records are encrypted at rest with zero data retention for third-party model training."},
            {"speaker": "Provost Campbell", "text": "That address our compliance mandate directly. Please proceed with the pilot deployment timeline."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "What central problem does SpeakUp AI solve according to Vikram's pitch?",
                "options": [
                    {"val": "a", "text": "Static language labs fail to build spontaneous conversational confidence"},
                    {"val": "b", "text": "Textbooks are too heavy to carry"},
                    {"val": "c", "text": "Students do not have computer access"}
                ],
                "correct": "a",
                "explanation": "Vikram stated that traditional language labs offer static audio but fail to build spontaneous spoken confidence."
            },
            {
                "q_id": 2,
                "question": "How are student audio streams processed to protect privacy?",
                "options": [
                    {"val": "a", "text": "In ephemeral memory with no persistent biometric voice storage and encrypted records"},
                    {"val": "b", "text": "They are uploaded to public video hosting channels"},
                    {"val": "c", "text": "They are sold to advertising networks"}
                ],
                "correct": "a",
                "explanation": "Vikram explained that audio is processed in ephemeral memory, encrypted at rest, with zero third-party retention."
            }
        ]
    },
    {
        "id": 13,
        "key": "prof_deadlines",
        "title": "Discussing Deadlines and Projects: Release Triage Sync",
        "category": "Professional",
        "category_slug": "professional",
        "difficulty": "Advanced",
        "duration": "~60 sec",
        "situation": "A release manager and principal engineer coordinate critical hotfix verification twelve hours prior to an enterprise cloud deployment.",
        "audio_text": "Team, we have twelve hours before the scheduled midnight maintenance window. What is the status of the connection leak issue in our database pool? The root cause was isolated to an unclosed cursor in the vocabulary lookup handler. A pull request with connection lifecycle guards and comprehensive unit tests is currently running through automated staging. How long will the automated load test suite require to certify the patch? The regression suite takes approximately forty-five minutes. Once green, our QA engineer will perform manual exploratory testing on the profile and settings endpoints. Very well. If all criteria pass by six PM, we authorize the midnight release. If any regression appears, we rollback cleanly and maintain our current stable version. Understood, release manager. We are monitoring the staging cluster closely.",
        "dialogue": [
            {"speaker": "Release Manager", "text": "Team, we have twelve hours before the scheduled midnight maintenance window. What is the status of the connection leak issue in our database pool?"},
            {"speaker": "Lead Engineer", "text": "The root cause was isolated to an unclosed cursor in the vocabulary lookup handler. A pull request with connection lifecycle guards and comprehensive unit tests is currently running through automated staging."},
            {"speaker": "Release Manager", "text": "How long will the automated load test suite require to certify the patch?"},
            {"speaker": "Lead Engineer", "text": "The regression suite takes approximately forty-five minutes. Once green, our QA engineer will perform manual exploratory testing on the profile and settings endpoints."},
            {"speaker": "Release Manager", "text": "Very well. If all criteria pass by six PM, we authorize the midnight release. If any regression appears, we rollback cleanly and maintain our current stable version."},
            {"speaker": "Lead Engineer", "text": "Understood, release manager. We are monitoring the staging cluster closely."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "What was the identified root cause of the database connection leak?",
                "options": [
                    {"val": "a", "text": "An unclosed cursor in the vocabulary lookup handler"},
                    {"val": "b", "text": "A hardware cable failure in the data center"},
                    {"val": "c", "text": "Incorrect user passwords entered at login"}
                ],
                "correct": "a",
                "explanation": "The lead engineer confirmed that the connection leak was caused by an unclosed cursor in the vocabulary lookup handler."
            },
            {
                "q_id": 2,
                "question": "What contingency plan did the release manager establish if regressions appear?",
                "options": [
                    {"val": "a", "text": "Execute a clean rollback and keep the current stable version"},
                    {"val": "b", "text": "Deploy anyway and fix bugs live in production"},
                    {"val": "c", "text": "Shut down the entire university network"}
                ],
                "correct": "a",
                "explanation": "The release manager stated that if any regression appears, they will rollback cleanly and maintain the current stable version."
            }
        ]
    },
    {
        "id": 14,
        "key": "prof_customer",
        "title": "Customer Service: Subscription & Licensing Resolution",
        "category": "Professional",
        "category_slug": "professional",
        "difficulty": "Intermediate",
        "duration": "~50 sec",
        "situation": "A support representative assists a college department coordinator who needs to upgrade concurrent student licenses without downtime.",
        "audio_text": "Thank you for contacting SpeakUp AI enterprise support. My name is Daniel. How can I help you today? Hello Daniel. I am the language department coordinator at Westlake College. We currently have a hundred student seats, but fifty additional students joined our conversational English elective this semester. We need to upgrade immediately. I would be happy to assist you with that. We can upgrade your tier to our Campus Pro package of two hundred seats right now. Your existing student records, streaks, and saved vocabulary will remain completely uninterrupted. That is fantastic news! Will the updated invoice reflect our academic institution discount? Yes, the twenty-five percent academic discount will be automatically applied to the prorated amount.",
        "dialogue": [
            {"speaker": "Daniel (Support)", "text": "Thank you for contacting SpeakUp AI enterprise support. My name is Daniel. How can I help you today?"},
            {"speaker": "Department Coordinator", "text": "Hello Daniel. I am the language department coordinator at Westlake College. We currently have a hundred student seats, but fifty additional students joined our conversational English elective this semester. We need to upgrade immediately."},
            {"speaker": "Daniel (Support)", "text": "I would be happy to assist you with that. We can upgrade your tier to our Campus Pro package of two hundred seats right now. Your existing student records, streaks, and saved vocabulary will remain completely uninterrupted."},
            {"speaker": "Department Coordinator", "text": "That is fantastic news! Will the updated invoice reflect our academic institution discount?"},
            {"speaker": "Daniel (Support)", "text": "Yes, the twenty-five percent academic discount will be automatically applied to the prorated amount."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "What guarantee did the support representative provide regarding existing student progress?",
                "options": [
                    {"val": "a", "text": "Student records, streaks, and saved vocabulary remain completely uninterrupted"},
                    {"val": "b", "text": "All student accounts must be deleted and created from scratch"},
                    {"val": "c", "text": "Students will lose their previous interview logs"}
                ],
                "correct": "a",
                "explanation": "Daniel reassured the coordinator that all existing student records, streaks, and saved vocabulary will remain uninterrupted."
            },
            {
                "q_id": 2,
                "question": "What discount will be applied to the college's prorated invoice?",
                "options": [
                    {"val": "a", "text": "A 25% academic institution discount"},
                    {"val": "b", "text": "A 5% holiday discount"},
                    {"val": "c", "text": "No discount is available for universities"}
                ],
                "correct": "a",
                "explanation": "Daniel confirmed that a 25% academic discount will be automatically applied."
            }
        ]
    },
    {
        "id": 15,
        "key": "prof_standup",
        "title": "Workplace Meetings: Engineering Stand-up & Cloud Migration",
        "category": "Professional",
        "category_slug": "professional",
        "difficulty": "Intermediate",
        "duration": "~55 sec",
        "situation": "Listen to a software team lead and DevOps engineer discussing sprint tasks, API deadlines, and security precautions ahead of client demonstrations.",
        "audio_text": "Team, quick update on our cloud sprint before tomorrow's demonstration. Vikram, where do we stand with the MySQL cloud migration? We have tested the read replicas and migrated the schemas, but we must verify that all connection credentials load from environment variables before our final cutover on Thursday end of day. Excellent precaution. Remember, secrets and API keys must never be committed to our version control repositories. Absolutely, Anita. All secret keys are managed through secure cloud vaults and injected dynamically into our deployment container.",
        "dialogue": [
            {"speaker": "Team Lead (Anita)", "text": "Team, quick update on our cloud sprint before tomorrow's demonstration. Vikram, where do we stand with the MySQL cloud migration?"},
            {"speaker": "DevOps Engineer (Vikram)", "text": "We have tested the read replicas and migrated the schemas, but we must verify that all connection credentials load from environment variables before our final cutover on Thursday end of day."},
            {"speaker": "Team Lead (Anita)", "text": "Excellent precaution. Remember, secrets and API keys must never be committed to our version control repositories."},
            {"speaker": "DevOps Engineer (Vikram)", "text": "Absolutely, Anita. All secret keys are managed through secure cloud vaults and injected dynamically into our deployment container."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "By what day must the database cutover be completed?",
                "options": [
                    {"val": "a", "text": "Tuesday morning"},
                    {"val": "b", "text": "Thursday end of day"},
                    {"val": "c", "text": "Friday after the demo"}
                ],
                "correct": "b",
                "explanation": "Vikram specifies that the final cutover is scheduled for Thursday end of day."
            },
            {
                "q_id": 2,
                "question": "What key security practice did the team emphasize regarding API keys and credentials?",
                "options": [
                    {"val": "a", "text": "Commit them directly in repository files"},
                    {"val": "b", "text": "Keep them securely in environment variables and secret vaults"},
                    {"val": "c", "text": "Email them in plain text to the team"}
                ],
                "correct": "b",
                "explanation": "Both the team lead and DevOps engineer emphasized loading credentials from environment variables and secret vaults rather than committing them."
            }
        ]
    },

    # ==========================================
    # 4. FRIENDLY CONVERSATIONS
    # ==========================================
    {
        "id": 16,
        "key": "friendly_intro",
        "title": "Introducing Yourself: Campus Student Tech Society Mixer",
        "category": "Friendly",
        "category_slug": "friendly",
        "difficulty": "Beginner",
        "duration": "~45 sec",
        "situation": "A second-year student introduces herself to an engineering peer at a campus tech club social mixer.",
        "audio_text": "Hi! Is anyone sitting here? No, go right ahead! I am Tariq. Nice to meet you, Tariq! I am Rhea. I saw your presentation on autonomous drones earlier; it was super interesting! Thank you so much! I have been building drones as a hobby for two years. What brought you to the tech society mixer tonight? I love web design and conversational AI. I am building a voice tutor that helps students practice spoken English before job interviews. Wow, that is a fantastic project! You should definitely showcase that at next month's student project showcase.",
        "dialogue": [
            {"speaker": "Rhea", "text": "Hi! Is anyone sitting here?"},
            {"speaker": "Tariq", "text": "No, go right ahead! I am Tariq."},
            {"speaker": "Rhea", "text": "Nice to meet you, Tariq! I am Rhea. I saw your presentation on autonomous drones earlier; it was super interesting!"},
            {"speaker": "Tariq", "text": "Thank you so much! I have been building drones as a hobby for two years. What brought you to the tech society mixer tonight?"},
            {"speaker": "Rhea", "text": "I love web design and conversational AI. I am building a voice tutor that helps students practice spoken English before job interviews."},
            {"speaker": "Tariq", "text": "Wow, that is a fantastic project! You should definitely showcase that at next month's student project showcase."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "What project is Rhea actively developing?",
                "options": [
                    {"val": "a", "text": "A voice AI tutor helping students practice spoken English for interviews"},
                    {"val": "b", "text": "A mechanical drone with solar panels"},
                    {"val": "c", "text": "A financial banking accounting spreadsheet"}
                ],
                "correct": "a",
                "explanation": "Rhea explained she is building a voice tutor that helps students practice spoken English before job interviews."
            },
            {
                "q_id": 2,
                "question": "What recommendation did Tariq give Rhea?",
                "options": [
                    {"val": "a", "text": "Showcase her voice AI tutor at next month's student showcase"},
                    {"val": "b", "text": "Stop coding and switch majors to biology"},
                    {"val": "c", "text": "Quit the tech club"}
                ],
                "correct": "a",
                "explanation": "Tariq praised the idea and encouraged her to showcase it at next month's student project exhibition."
            }
        ]
    },
    {
        "id": 17,
        "key": "friendly_helping",
        "title": "Helping Someone: Debugging Python Algorithm Logic",
        "category": "Friendly",
        "category_slug": "friendly",
        "difficulty": "Beginner",
        "duration": "~45 sec",
        "situation": "A peer tutor helps a junior classmate identify an off-by-one index error in their recursive binary search program.",
        "audio_text": "Hey Jay, could you glance at my code for a second? My recursive search keeps throwing an index out of bounds error. Sure, let me take a look. Show me your base condition. Here on line fourteen, I check if high is greater than low. Ah, look closely at line nineteen where you calculate mid. You have written high minus low without adding low back, and your loop condition should be low less than or equal to high. Oh! That makes complete sense. I was calculating the offset instead of the actual array index. Exactly. Fix that calculation and rerun your unit test. Look at that, all test assertions passed! Thank you so much, Jay; you saved me hours of frustration.",
        "dialogue": [
            {"speaker": "Junior Student", "text": "Hey Jay, could you glance at my code for a second? My recursive search keeps throwing an index out of bounds error."},
            {"speaker": "Jay (Tutor)", "text": "Sure, let me take a look. Show me your base condition."},
            {"speaker": "Junior Student", "text": "Here on line fourteen, I check if high is greater than low."},
            {"speaker": "Jay (Tutor)", "text": "Ah, look closely at line nineteen where you calculate mid. You have written high minus low without adding low back, and your loop condition should be low less than or equal to high."},
            {"speaker": "Junior Student", "text": "Oh! That makes complete sense. I was calculating the offset instead of the actual array index."},
            {"speaker": "Jay (Tutor)", "text": "Exactly. Fix that calculation and rerun your unit test. Look at that, all test assertions passed! Thank you so much, Jay; you saved me hours of frustration."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "What was the logical bug causing the index out of bounds error?",
                "options": [
                    {"val": "a", "text": "Incorrect mid-point calculation and loop boundary condition"},
                    {"val": "b", "text": "A syntax error due to a missing semicolon"},
                    {"val": "c", "text": "The computer had run out of disk storage"}
                ],
                "correct": "a",
                "explanation": "Jay noticed that the mid calculation on line 19 calculated only the offset and the condition needed to be low <= high."
            },
            {
                "q_id": 2,
                "question": "What happened after applying Jay's suggested correction?",
                "options": [
                    {"val": "a", "text": "All test assertions passed successfully"},
                    {"val": "b", "text": "The computer restarted automatically"},
                    {"val": "c", "text": "The program crashed again with a syntax error"}
                ],
                "correct": "a",
                "explanation": "The student re-ran the unit tests and confirmed that all test assertions passed cleanly."
            }
        ]
    },
    {
        "id": 18,
        "key": "friendly_suggestions",
        "title": "Giving Suggestions: Building Effective Spoken Habits",
        "category": "Friendly",
        "category_slug": "friendly",
        "difficulty": "Intermediate",
        "duration": "~50 sec",
        "situation": "A fluent student shares three actionable daily speaking techniques with a classmate preparing for campus placements.",
        "audio_text": "Hey Aman, you always sound so articulate and natural during class presentations. How did you overcome hesitation? Honestly, Priya, I used to freeze whenever professors asked me questions. What helped me was practicing shadowing for ten minutes every morning. Shadowing? How does that work? You listen to short native audio clips and speak the words aloud immediately after hearing them, matching the rhythm and intonation. That trains your mouth muscles. That sounds practical. Do you also recommend keeping a vocabulary notebook? Definitely. But instead of memorizing isolated words, write down entire three-word collocations, like 'reach a consensus' or 'address a bottleneck'. I am starting that routine tonight! Thanks for the encouragement, Aman.",
        "dialogue": [
            {"speaker": "Priya", "text": "Hey Aman, you always sound so articulate and natural during class presentations. How did you overcome hesitation?"},
            {"speaker": "Aman", "text": "Honestly, Priya, I used to freeze whenever professors asked me questions. What helped me was practicing shadowing for ten minutes every morning."},
            {"speaker": "Priya", "text": "Shadowing? How does that work?"},
            {"speaker": "Aman", "text": "You listen to short native audio clips and speak the words aloud immediately after hearing them, matching the rhythm and intonation. That trains your mouth muscles."},
            {"speaker": "Priya", "text": "That sounds practical. Do you also recommend keeping a vocabulary notebook?"},
            {"speaker": "Aman", "text": "Definitely. But instead of memorizing isolated words, write down entire three-word collocations, like 'reach a consensus' or 'address a bottleneck'."},
            {"speaker": "Priya", "text": "I am starting that routine tonight! Thanks for the encouragement, Aman."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "How does the 'shadowing' practice technique work according to Aman?",
                "options": [
                    {"val": "a", "text": "Speaking words aloud immediately after listening to audio to match rhythm and intonation"},
                    {"val": "b", "text": "Silently reading a grammar book before bedtime"},
                    {"val": "c", "text": "Memorizing 50 disconnected dictionary words per day"}
                ],
                "correct": "a",
                "explanation": "Aman explains that shadowing involves repeating audio immediately aloud, matching rhythm and intonation."
            },
            {
                "q_id": 2,
                "question": "What advice does Aman give regarding vocabulary learning?",
                "options": [
                    {"val": "a", "text": "Write down whole collocations and phrases rather than isolated single words"},
                    {"val": "b", "text": "Only learn words from classical literature"},
                    {"val": "c", "text": "Never review previously saved words"}
                ],
                "correct": "a",
                "explanation": "Aman advised writing down multi-word collocations (e.g. 'reach a consensus') instead of isolated individual words."
            }
        ]
    },
    {
        "id": 19,
        "key": "friendly_plans",
        "title": "Making Plans with Friends: 24-Hour Hackathon Squad",
        "category": "Friendly",
        "category_slug": "friendly",
        "difficulty": "Intermediate",
        "duration": "~50 sec",
        "situation": "Three college friends divide technical tasks, assign UI prototyping, and set target milestones for an upcoming weekend hackathon.",
        "audio_text": "Alright team, registration for the Innovation Hackathon closes tonight. Are we finalized on building an automated resume reviewer? Yes, let us commit to it! How should we divide our roles for the twenty-four hours? I propose Kabir handles the backend API and database schemas, Sara owns the front-end user dashboard in Tailwind and HTML, and I will focus on prompt engineering and the evaluation rubric. That is a well-balanced distribution. Let us set a milestone: complete our database and wireframes by midnight, so we have all Sunday morning for stress testing and pitch rehearsal. Perfect. I will bring extension cords and snacks. Let us aim for the podium this weekend!",
        "dialogue": [
            {"speaker": "Kavita", "text": "Alright team, registration for the Innovation Hackathon closes tonight. Are we finalized on building an automated resume reviewer?"},
            {"speaker": "Sara", "text": "Yes, let us commit to it! How should we divide our roles for the twenty-four hours?"},
            {"speaker": "Kabir", "text": "I propose Kabir handles the backend API and database schemas, Sara owns the front-end user dashboard in Tailwind and HTML, and I will focus on prompt engineering and the evaluation rubric."},
            {"speaker": "Kavita", "text": "That is a well-balanced distribution. Let us set a milestone: complete our database and wireframes by midnight, so we have all Sunday morning for stress testing and pitch rehearsal."},
            {"speaker": "Sara", "text": "Perfect. I will bring extension cords and snacks. Let us aim for the podium this weekend!"}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "What project will the team build during the 24-hour hackathon?",
                "options": [
                    {"val": "a", "text": "An automated resume reviewer web application"},
                    {"val": "b", "text": "A multiplayer smartphone gaming app"},
                    {"val": "c", "text": "An online shoe shopping store"}
                ],
                "correct": "a",
                "explanation": "Kavita confirms that the team has finalized on building an automated resume reviewer."
            },
            {
                "q_id": 2,
                "question": "What milestone target did the team establish for midnight?",
                "options": [
                    {"val": "a", "text": "Complete the database schema and frontend wireframes"},
                    {"val": "b", "text": "Give the final presentation to judges"},
                    {"val": "c", "text": "Pack up and go home early"}
                ],
                "correct": "a",
                "explanation": "Kavita proposed completing the database and wireframes by midnight to leave Sunday morning for testing."
            }
        ]
    },
    {
        "id": 20,
        "key": "friendly_opinions",
        "title": "Expressing Opinions Politely: Remote vs In-Office Work",
        "category": "Friendly",
        "category_slug": "friendly",
        "difficulty": "Advanced",
        "duration": "~60 sec",
        "situation": "Two software interns exchange constructive perspectives on flexible hybrid schedules, team culture, and deep focus time without conflict.",
        "audio_text": "Neil, what are your thoughts on companies mandating a full return to physical offices? In my view, while in-person whiteboarding fosters immediate camaraderie, mandatory five-day office requirements disregard the productivity gains of deep focus time at home. I see your point regarding deep focus, Neil. However, from my perspective, junior engineers often struggle in purely remote environments because they miss out on spontaneous hallway mentorship and observing how senior leads resolve problems. That is a very valid distinction, Leah. Perhaps the ideal compromise is a structured hybrid model: two collaborative days in the office for sprint planning and design critiques, paired with three remote days for uninterrupted coding. Exactly. It respects autonomy while nurturing team cohesion.",
        "dialogue": [
            {"speaker": "Leah", "text": "Neil, what are your thoughts on companies mandating a full return to physical offices?"},
            {"speaker": "Neil", "text": "In my view, while in-person whiteboarding fosters immediate camaraderie, mandatory five-day office requirements disregard the productivity gains of deep focus time at home."},
            {"speaker": "Leah", "text": "I see your point regarding deep focus, Neil. However, from my perspective, junior engineers often struggle in purely remote environments because they miss out on spontaneous hallway mentorship and observing how senior leads resolve problems."},
            {"speaker": "Neil", "text": "That is a very valid distinction, Leah. Perhaps the ideal compromise is a structured hybrid model: two collaborative days in the office for sprint planning and design critiques, paired with three remote days for uninterrupted coding."},
            {"speaker": "Leah", "text": "Exactly. It respects autonomy while nurturing team cohesion."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "What specific drawback of purely remote work did Leah highlight for junior engineers?",
                "options": [
                    {"val": "a", "text": "Missing out on spontaneous hallway mentorship and observing senior leaders"},
                    {"val": "b", "text": "Higher internet electricity bills"},
                    {"val": "c", "text": "Lack of free office coffee"}
                ],
                "correct": "a",
                "explanation": "Leah explained that junior engineers can struggle remotely because they miss spontaneous mentorship and problem-solving observation."
            },
            {
                "q_id": 2,
                "question": "What balanced compromise did Neil and Leah agree upon?",
                "options": [
                    {"val": "a", "text": "A structured hybrid model: 2 collaborative office days and 3 remote focus days"},
                    {"val": "b", "text": "Working 7 days a week from the office"},
                    {"val": "c", "text": "Closing all offices permanently"}
                ],
                "correct": "a",
                "explanation": "They agreed on a hybrid model combining 2 office collaboration days with 3 remote deep-focus days."
            }
        ]
    },
    {
        "id": 21,
        "key": "friendly_cafe",
        "title": "Friendly Interactions: The Green Bean Cafe Order",
        "category": "Friendly",
        "category_slug": "friendly",
        "difficulty": "Beginner",
        "duration": "~45 sec",
        "situation": "Listen to a customer placing a customized coffee order with barista Sophia. Pay attention to milk choices and extras requested.",
        "audio_text": "Good morning! Welcome to The Green Bean Cafe. What can I prepare fresh for you today? Hi there! I would love a regular cappuccino, but could you please make that with warm oat milk? Certainly! Would you like any pastry or snack with that today? Yes, could you please warm up a fresh butter croissant to go? Absolutely! One oat cappuccino and a warm butter croissant coming right up. That will be four dollars and fifty cents.",
        "dialogue": [
            {"speaker": "Barista (Sophia)", "text": "Good morning! Welcome to The Green Bean Cafe. What can I prepare fresh for you today?"},
            {"speaker": "Customer", "text": "Hi there! I would love a regular cappuccino, but could you please make that with warm oat milk?"},
            {"speaker": "Barista (Sophia)", "text": "Certainly! Would you like any pastry or snack with that today?"},
            {"speaker": "Customer", "text": "Yes, could you please warm up a fresh butter croissant to go?"},
            {"speaker": "Barista (Sophia)", "text": "Absolutely! One oat cappuccino and a warm butter croissant coming right up. That will be four dollars and fifty cents."}
        ],
        "questions": [
            {
                "q_id": 1,
                "question": "What type of milk did the customer specifically ask for?",
                "options": [
                    {"val": "a", "text": "Whole dairy milk"},
                    {"val": "b", "text": "Warm oat milk"},
                    {"val": "c", "text": "Unsweetened almond milk"}
                ],
                "correct": "b",
                "explanation": "The customer requested a cappuccino made with warm oat milk."
            },
            {
                "q_id": 2,
                "question": "What bakery item was added to the order?",
                "options": [
                    {"val": "a", "text": "Blueberry muffin"},
                    {"val": "b", "text": "Warm butter croissant"},
                    {"val": "c", "text": "Chocolate chip cookie"}
                ],
                "correct": "b",
                "explanation": "The customer asked to warm up a fresh butter croissant to go."
            }
        ]
    }
]
