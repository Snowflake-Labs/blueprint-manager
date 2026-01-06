import os
import sys
import yaml


def load_answers(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def validate_answers(answers):
    unanswered_questions = []
    for key, value in answers.items():
        if value == 'TODO':
            unanswered_questions.append(key)
    return unanswered_questions


def main(workflow_id, answers_file):
    answers = load_answers(answers_file)
    unanswered_questions = validate_answers(answers)
    if unanswered_questions:
        print('The following questions were not answered:')
        for question in unanswered_questions:
            print(f'- {question}')
        sys.exit(1)
    else:
        print('All questions were answered.')
        # Proceed with rendering the journey
        # render_journey(workflow_id, answers)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Render a journey based on workflow and answers.')
    parser.add_argument('--workflow', required=True, help='The workflow ID')
    parser.add_argument('--answers', required=True, help='The path to the answers file')
    args = parser.parse_args()
    main(args.workflow, args.answers)