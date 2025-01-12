#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# to run this script you need to
# pip install python-gitlab

import argparse
import os
import re
import sys
from pathlib import Path

import gitlab

SEC_PER_H = 3600.0
WORK_H_PER_WEEK = 39.0


def calculate_time(issues):
    """sum up total time spent from the issues provided"""
    time_spent_sec = 0
    for issue in issues:
        time_spent_sec += issue.time_stats()["total_time_spent"]

    time_spent_weeks = time_spent_sec / SEC_PER_H / WORK_H_PER_WEEK
    time_spent_percentage = round(time_spent_weeks / total_weeks * 100, 2)

    progress_bar = generate_progress_bar(time_spent_percentage)

    time_text = f"""{progress_bar}

Total time available: {total_weeks} weeks

Total time spent: {round(time_spent_weeks,2)} weeks"""

    return time_text


def generate_progress_bar(percentage, width=50):
    """ """

    fill_elem = "█"
    padding = "-"

    if percentage > 100:
        percentage = 100

    step_size = 100 / width
    num_fill_elem = int(percentage / step_size)

    bar = fill_elem * num_fill_elem + padding * (width - num_fill_elem)
    bar_str = f"Progress |{bar}| {percentage}% Complete"

    return bar_str


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
													Generate amount of total time spent on a project.
													Make sure that PRIVATE_TOKEN, PROJECT_ID and TOTAL_WEEKS are
													defined as environment variables. Example:
													 PRIVATE_TOKEN=qzomQFXR5Bkys5j2u5yS PROJECT_ID=1288 TOTAL_WEEKS=1.7 ./total_time_spent.py -r

												"""
    )

    parser.add_argument(
        "-pt",
        "--private-token",
        required=True,
        type=str,
        help="""
				obtain PRIVATE_TOKEN:  Your_Project->Settings->Access Token->read_api. Paste value here.
				e.g GxNVhy3GVezwTRMWUgXP
			""",
    )

    parser.add_argument(
        "-pi",
        "--project-id",
        required=True,
        type=int,
        help="""
				obtain PROJECT_ID: You can find the prject id right on your projects main-page, below the icon. Paste value here.
				e.g 2934
			""",
    )

    parser.add_argument(
        "-w",
        "--weeks",
        required=True,
        type=float,
        help="""
			Add the originally estimated duration value here. e.g 1.5, 2.0
		""",
    )
    parser.add_argument(
        "-r",
        "--to-readme",
        action="store_true",
        default=False,
        help="Insert the generated output into the project's README.md",
    )

    parser.add_argument(
        "-pr",
        "--path-to-readme",
        action="store",
        type=Path,
        default=Path("./README.md"),
        help="specify the readme to use here",
    )

    args = parser.parse_args()
    to_readme = args.to_readme
    private_token = args.private_token
    project_id = args.project_id
    total_weeks = args.weeks
    gitlab_url = "http://gitlab.hzdr.de"

    # for private_token create a private read-only token (Settings->Access Tokens) for your project.
    gl = gitlab.Gitlab(gitlab_url, private_token)  # ='9mZzS1zfXEeiWd-AvLBa')

    project = gl.projects.get(project_id)

    issues = project.issues.list(all=True)

    time_text = calculate_time(issues)
    print(time_text)

    if to_readme:
        expression = "^Progress \|.*$"
        with open("README.md", "r+") as f:
            readme_text = f.read().split("\n")

            line_nr_progress_bar = -1
            for i, line in enumerate(readme_text):
                if re.search(expression, line) is not None:
                    line_nr_progress_bar = i
                    break

            if line_nr_progress_bar == -1:
                print(
                    "README.md does not contain progress bar. Inserting at beginning of file.."
                )
                line_nr_progress_bar = 0

            # overwrite existing progress bar
            time_text = time_text.split("\n")
            for i in range(len(time_text)):
                readme_text[i + line_nr_progress_bar] = time_text[i]

            f.seek(0)
            f.write("\n".join(readme_text))
