import streamlit as st
import os
from snowflake_local.connection import session
from snowflake_local.rag import complete
import json

def generate_quiz():
    
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = []
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = []
    if "correct_answers" not in st.session_state:
        st.session_state.correct_answers = []
    if "is_quiz_generated" not in st.session_state:
        st.session_state.is_quiz_generated = False
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    st.subheader("Generate Interactive Quiz from Documents")

   
    try:
        docs = session.sql("LIST @docs").collect()
        doc_list = [os.path.basename(doc["name"]) for doc in docs]

        if not doc_list:
            st.warning("No documents found in the Snowflake stage.")
            return
    except Exception as e:
        st.error(f"Failed to fetch documents: {e}")
        return

    
    selected_doc = st.selectbox("Choose a document for the quiz", doc_list)

    
    difficulty = st.selectbox("Select quiz difficulty:", ["Easy", "Medium", "Hard"])

    if selected_doc:
        
        if st.button("Generate Quiz"):
            
            prompt = (
                f"Generate 5 objective type questions from {selected_doc}, "
                f"in the format '{{"
                f"\"1\":{{"
                f"\"Question\": \"\", "
                f"\"Answer\": \"\", "
                f"\"Options\": [\"\", \"\", \"\", \"\"]}}}}' as a JSON object. "
                f"The difficulty level should be {difficulty}. Be very precise in the answer."
            )

            try:
               
                result, _ = complete(prompt)
                response = result[0].RESPONSE

                
                data = json.loads(response)
                quiz = []
                for key, value in data.items():
                    if (
                        "Question" in value
                        and "Answer" in value
                        and "Options" in value
                        and isinstance(value["Options"], list)
                    ):
                        quiz.append({
                            "Question": value["Question"],
                            "Answer": value["Answer"],
                            "Options": value["Options"]
                        })
                    else:
                        st.error(f"Invalid format for Question {key}. Please try again.")
                        return


                st.session_state.quiz_data = quiz
                st.session_state.user_answers = [None] * len(quiz)
                st.session_state.correct_answers = [False] * len(quiz)
                st.session_state.is_quiz_generated = True
                st.session_state.quiz_submitted = False

            except (json.JSONDecodeError, KeyError) as e:
                st.error(f"Failed to parse the response: {e}")
                st.write("Debug Response:", response)
                return
            except Exception as e:
                st.error(f"Error generating quiz: {e}")
                return

    if st.session_state.is_quiz_generated:
        quiz = st.session_state.quiz_data

        for i, question in enumerate(quiz):
            st.write(f"**Question {i + 1}:** {question['Question']}")
            st.session_state.user_answers[i] = st.radio(
                f"Select an option for Question {i + 1}:",
                question["Options"],
                index=0 if st.session_state.user_answers[i] is None else question["Options"].index(st.session_state.user_answers[i]),
                key=f"question_{i}"
            )
        
        if st.button("Submit Quiz") and not st.session_state.quiz_submitted:
            st.session_state.quiz_submitted = True
            for i, question in enumerate(quiz):
                st.session_state.correct_answers[i] = st.session_state.user_answers[i] == question["Answer"]

        
        if st.session_state.quiz_submitted:
            total_correct = 0
            for i, question in enumerate(quiz):
                if st.session_state.correct_answers[i]:
                    st.success(f"Correct! ✅ Question {i + 1}: {question['Question']}")
                    total_correct += 1
                else:
                    st.error(f"Wrong ❌ Question {i + 1}: {question['Question']}")
                    st.info(f"The correct answer is: {question['Answer']}")

            
            st.write(f"### Final Score: {total_correct} out of {len(quiz)}")

