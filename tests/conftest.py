"""
Shared test fixtures for resume automation tests.
This module provides common test fixtures used across multiple test modules.
"""

import pytest
from pathlib import Path
from src.parser import ResumeSection


@pytest.fixture
def sample_markdown_content() -> str:
    """
    Provide sample markdown resume content for testing.
    
    Returns:
        str: Sample markdown resume content
    """
    return """# John Smith

john.smith@email.com • San Francisco, California • [LinkedIn](https://linkedin.com/in/johnsmith) • [GitHub](https://github.com/johnsmith)

## Summary

Senior Software Engineer with 8+ years developing scalable web applications and leading cross-functional teams. Proven track record of delivering high-impact solutions that improve system performance and user experience. Expertise in Python, JavaScript, and cloud technologies with a focus on microservices architecture and DevOps practices.

## Technical Skills

**Languages:** Python, JavaScript, TypeScript, Java, SQL, Go, Bash
**Frontend:** React, Vue.js, Angular, HTML5, CSS3, Tailwind CSS
**Backend:** Django, Flask, Node.js, Express.js, FastAPI, Spring Boot
**Databases:** PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch
**Cloud & DevOps:** AWS, Azure, Docker, Kubernetes, Jenkins, Terraform
**Tools:** Git, GitHub Actions, JIRA, Slack, Postman, VS Code

## Professional Experience

### Microservices Migration & Platform Modernization

**Technologies:** Python, Django, Docker, Kubernetes, PostgreSQL, Redis, Jenkins, AWS
_January 2020 - Present_

- Architected and led migration of monolithic e-commerce platform to microservices architecture, reducing deployment time by 60% and improving system scalability to handle 10M+ daily requests
- Designed event-driven architecture using Apache Kafka for inter-service communication, enabling real-time data processing and improving system reliability by 99.9% uptime
- Implemented comprehensive CI/CD pipeline using Jenkins and Docker, automating testing and deployment for 15+ development teams with zero-downtime deployments
- Built advanced monitoring and observability stack using Prometheus, Grafana, and ELK stack, reducing mean time to resolution by 45%

## Education

### B.S. Computer Science | State University

**2013 - 2017**

- **GPA:** 3.7/4.0
- **Relevant Coursework:** Data Structures, Algorithms, Database Systems, Software Engineering, Computer Networks
- **Senior Project:** Built a web-based task management application using Django and React with real-time collaboration features
"""


@pytest.fixture
def sample_resume_section() -> ResumeSection:
    """
    Provide sample ResumeSection for testing.
    
    Returns:
        ResumeSection: Sample resume section with test data
    """
    return ResumeSection(
        title="Experience",
        content=[
            "Senior Software Engineer | TechCorp Inc.",
            "January 2020 - Present",
            "- Led migration of monolithic application to microservices architecture",
            "- Implemented CI/CD pipeline reducing deployment time by 60%",
        ],
        level=2,
        metadata={"section_type": "experience", "company": "TechCorp Inc."}
    )


@pytest.fixture
def sample_resume_sections() -> dict[str, ResumeSection]:
    """
    Provide sample dictionary of resume sections for testing.
    
    Returns:
        Dict[str, ResumeSection]: Dictionary of sample resume sections
    """
    return {
        "summary": ResumeSection(
            title="Summary",
            content=[
                "Senior Software Engineer with 8+ years developing scalable web applications"
            ],
            level=2
        ),
        "experience": ResumeSection(
            title="Experience",
            content=[
                "Senior Software Engineer | TechCorp Inc.",
                "January 2020 - Present",
                "- Led migration of monolithic application to microservices architecture",
            ],
            level=2
        ),
        "education": ResumeSection(
            title="Education",
            content=[
                "B.S. Computer Science | State University",
                "2013 - 2017",
                "- GPA: 3.7/4.0",
            ],
            level=2
        )
    }


@pytest.fixture
def sample_markdown_file(tmp_path: Path) -> Path:
    """
    Create a temporary markdown file for testing.
    
    Args:
        tmp_path: Pytest temporary directory fixture
        
    Returns:
        Path: Path to the temporary markdown file
    """
    markdown_file = tmp_path / "test_resume.md"
    markdown_file.write_text("""# Test Resume

## Summary
Test summary content

## Experience
Test experience content
""")
    return markdown_file