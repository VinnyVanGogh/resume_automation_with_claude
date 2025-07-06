"""
Integration tests for the resume automation pipeline.
"""

import pytest
import tempfile
import os
from src.parser import MarkdownResumeParser
from src.validation import ResumeValidator
from src.models import ResumeData
from src.custom_types import InvalidMarkdownError


class TestEndToEndParsing:
    """End-to-end integration tests for resume parsing."""

    def test_complete_resume_parsing_flow(self):
        """Test complete resume parsing from markdown to validated data."""
        parser = MarkdownResumeParser()
        
        complete_resume = """
# Dr. Sarah Chen
sarah.chen@techcorp.com | +1 (555) 123-4567
https://linkedin.com/in/sarahchen | https://github.com/sarahchen
https://sarahchen.dev

## Summary

Senior Software Engineer with 8+ years of experience in full-stack development, 
specializing in cloud architecture and machine learning applications. Proven track 
record of leading cross-functional teams and delivering scalable solutions.

## Experience

### Staff Software Engineer at Google
March 2021 - Present | Mountain View, CA
- Led development of microservices architecture serving 100M+ users daily
- Implemented ML-powered recommendation system increasing user engagement by 35%
- Mentored team of 8 engineers and established best practices for code quality
- Reduced system latency by 60% through performance optimization initiatives

### Senior Software Engineer at Facebook
June 2018 - February 2021 | Menlo Park, CA
- Built real-time data processing pipelines handling 50TB+ of data daily
- Developed React-based analytics dashboard used by 1000+ internal stakeholders
- Collaborated with product teams to deliver 15+ feature releases quarterly
- Improved deployment pipeline reducing release time from 4 hours to 30 minutes

### Software Engineer at Uber
January 2016 - May 2018 | San Francisco, CA
- Designed and implemented core payment processing system
- Created automated testing framework reducing bug detection time by 70%
- Optimized database queries improving application response time by 45%

## Education

### Master of Science in Computer Science
Stanford University | 2014-2016
- Specialization: Machine Learning and Artificial Intelligence
- GPA: 3.9/4.0
- Thesis: "Deep Learning Approaches for Real-time Image Recognition"

### Bachelor of Science in Computer Engineering
UC Berkeley | 2010-2014
- Magna Cum Laude, Phi Beta Kappa
- GPA: 3.8/4.0
- Relevant Coursework: Data Structures, Algorithms, Software Engineering

## Skills

### Programming Languages:
Python, Java, JavaScript, TypeScript, Go, Scala, C++

### Frameworks & Libraries:
React, Node.js, Django, Spring Boot, TensorFlow, PyTorch, Kafka

### Cloud & Infrastructure:
AWS, Google Cloud Platform, Kubernetes, Docker, Terraform

### Databases:
PostgreSQL, MongoDB, Redis, Elasticsearch, BigQuery

### Tools & Technologies:
Git, Jenkins, Prometheus, Grafana, Apache Spark

## Projects

### Open Source Contributions
- Core contributor to TensorFlow (500+ commits)
- Maintainer of popular Python library for data processing (10k+ stars on GitHub)
- Speaker at 5+ tech conferences including PyCon and NeurIPS

### Personal Projects
- Built ML-powered stock prediction app with 95% accuracy rate
- Created automated investment portfolio optimizer using reinforcement learning
- Developed Chrome extension for productivity tracking (50k+ active users)

## Certifications

### AWS Certified Solutions Architect - Professional
Amazon Web Services | 2022
Credential ID: AWS-SAP-2022-SC789

### Google Cloud Professional Data Engineer
Google Cloud | 2021
Credential ID: GCP-PDE-2021-SC456
"""
        
        # Test parsing without validation first
        result = parser.parse(complete_resume, validate_result=False)
        
        # Verify all sections were parsed correctly
        assert isinstance(result, ResumeData)
        assert result.contact.name == "Dr. Sarah Chen"
        assert result.contact.email == "sarah.chen@techcorp.com"
        assert result.contact.phone == "+1 (555) 123-4567"
        assert "linkedin.com/in/sarahchen" in str(result.contact.linkedin)
        assert "github.com/sarahchen" in str(result.contact.github)
        assert "sarahchen.dev" in str(result.contact.website)
        
        # Verify summary
        assert result.summary is not None
        assert "Senior Software Engineer" in result.summary
        assert "8+ years" in result.summary
        
        # Verify experience
        assert len(result.experience) == 3
        exp_titles = [exp.title for exp in result.experience]
        assert "Staff Software Engineer" in exp_titles
        assert "Senior Software Engineer" in exp_titles
        assert "Software Engineer" in exp_titles
        
        # Verify education
        assert len(result.education) == 2
        degrees = [edu.degree for edu in result.education]
        assert any("Master" in degree for degree in degrees)
        assert any("Bachelor" in degree for degree in degrees)
        
        # Verify skills
        assert result.skills is not None
        assert result.skills.categories is not None
        assert len(result.skills.categories) >= 5
        
        # Test with validation enabled
        validated_result, warnings = parser.parse_with_warnings(complete_resume)
        assert len(warnings) == 0  # Should be a high-quality resume with no warnings

    def test_minimal_valid_resume(self):
        """Test parsing minimal but valid resume."""
        parser = MarkdownResumeParser(strict_validation=False)
        
        minimal_resume = """
# Alex Johnson
alex.johnson@email.com | (555) 987-6543

## Summary
Recent graduate with strong programming skills.

## Experience

### Junior Developer at StartupCo
June 2023 - Present
- Developed web applications using React and Node.js
- Collaborated with design team on user interface improvements
- Participated in code reviews and agile development processes

## Education

### Bachelor of Science in Computer Science
State University | 2019-2023
- GPA: 3.5/4.0
- Relevant coursework: Data Structures, Web Development, Database Systems

## Skills

### Programming:
JavaScript, Python, HTML, CSS, SQL

### Tools:
Git, VS Code, npm, MySQL
"""
        
        result, warnings = parser.parse_with_warnings(minimal_resume)
        
        # Should parse successfully
        assert result.contact.name == "Alex Johnson"
        assert len(result.experience) == 1
        assert len(result.education) == 1
        assert result.skills is not None
        
        # May have some warnings but should be valid
        assert isinstance(warnings, list)

    def test_parser_with_various_markdown_formats(self):
        """Test parser handles various markdown formatting styles."""
        parser = MarkdownResumeParser(validate_input=False)
        
        # Test different heading styles
        different_formats = [
            # Format 1: Standard format
            """
# John Doe
john@example.com

## Experience
### Software Engineer - TechCorp
- Built applications
""",
            # Format 2: Contact info in separate lines
            """
# Jane Smith
jane@example.com
Phone: (555) 123-4567
LinkedIn: https://linkedin.com/in/jane

## Work Experience
**Senior Developer** | *MegaCorp* | 2020-Present
• Led development team
• Improved system performance
""",
            # Format 3: Mixed bullet styles
            """
# Bob Wilson
bob@example.com

## Professional Experience

### Lead Engineer
**Company:** TechStart
**Duration:** 2021-2024
* Designed microservices architecture
* Mentored junior developers
+ Increased team productivity by 40%
"""
        ]
        
        for i, resume_format in enumerate(different_formats):
            try:
                result = parser.parse(resume_format)
                assert result.contact.name is not None
                # Basic validation that parsing didn't crash
            except Exception as e:
                pytest.fail(f"Format {i+1} failed to parse: {e}")

    def test_real_world_resume_samples(self):
        """Test parsing with realistic resume variations."""
        parser = MarkdownResumeParser(validate_input=False)
        
        # Sample 1: Academic resume
        academic_resume = """
# Dr. Maria Rodriguez, Ph.D.
maria.rodriguez@university.edu | Office: (555) 123-4567
https://linkedin.com/in/mariarodriguez | ORCID: 0000-0000-0000-0000

## Academic Appointments

### Assistant Professor of Computer Science
University of Technology | 2020 - Present
- Teaching: Data Structures, Machine Learning, Research Methods
- Research: Natural Language Processing, Deep Learning Applications
- Publications: 15 peer-reviewed papers, 3 conference presentations

### Postdoctoral Research Fellow  
Institute for AI Research | 2018 - 2020
- Conducted research on neural network optimization
- Collaborated with industry partners on applied ML projects

## Education

### Ph.D. in Computer Science
MIT | 2014 - 2018
- Dissertation: "Efficient Neural Architecture Search for Edge Computing"
- Advisor: Prof. John Smith

### M.S. in Computer Science
Carnegie Mellon University | 2012 - 2014

## Skills
Python, TensorFlow, PyTorch, R, MATLAB, LaTeX
"""
        
        # Sample 2: Career changer resume
        career_change_resume = """
# Michael Chang
michael.chang@email.com | (555) 789-0123

## Summary
Former marketing professional transitioning to software development. 
Completed intensive coding bootcamp and built several web applications.

## Technical Experience

### Full Stack Developer (Freelance)
Self-Employed | 2023 - Present
- Built e-commerce website for local business using MERN stack
- Created inventory management system with React and Express
- Implemented user authentication and payment processing

## Previous Experience

### Marketing Manager
RetailCorp | 2018 - 2023
- Managed digital marketing campaigns with $500K+ budget
- Analyzed customer data to optimize conversion rates
- Led cross-functional team of 5 marketing specialists

## Education

### Full Stack Web Development Bootcamp
TechAcademy | 2023
- 600-hour intensive program covering JavaScript, React, Node.js
- Capstone project: Task management application

### Bachelor of Arts in Marketing
Business University | 2014 - 2018
"""
        
        real_world_samples = [academic_resume, career_change_resume]
        
        for i, sample in enumerate(real_world_samples):
            try:
                result = parser.parse(sample)
                assert result.contact.name is not None
                assert result.contact.email is not None
                # Should handle different resume styles gracefully
            except Exception as e:
                pytest.fail(f"Real-world sample {i+1} failed to parse: {e}")

    def test_parser_error_recovery(self):
        """Test parser error handling and recovery."""
        parser = MarkdownResumeParser()
        
        # Test various problematic inputs that should fail
        problematic_inputs = [
            "",  # Empty
            "Just some random text",  # No structure
            "# Name\nno-email",  # Missing email
            "# \n@invalid-email",  # Invalid email format
        ]
        
        for problematic_input in problematic_inputs:
            with pytest.raises(InvalidMarkdownError):
                parser.parse(problematic_input)

    def test_performance_with_large_resume(self):
        """Test parser performance with large resume."""
        parser = MarkdownResumeParser(validate_input=False)
        
        # Generate a large resume
        large_resume = """
# Performance Test User
perf.test@example.com

## Summary
""" + "Long summary paragraph. " * 50 + """

## Experience
"""
        
        # Add 20 experience entries
        for i in range(20):
            large_resume += f"""
### Senior Engineer {i+1}
Company {i+1} | 2020-202{i%4}
""" + "\n".join([f"- Achievement {j+1} for position {i+1}" for j in range(10)]) + "\n"
        
        large_resume += """
## Education
"""
        
        # Add multiple education entries
        for i in range(5):
            large_resume += f"""
### Degree {i+1}
University {i+1} | 2015-201{5+i%4}
"""
        
        large_resume += """
## Skills
""" + "\n".join([f"- Skill {i+1}" for i in range(100)])
        
        # Should handle large resume without performance issues
        import time
        start_time = time.time()
        result = parser.parse(large_resume)
        end_time = time.time()
        
        # Should complete within reasonable time (< 5 seconds)
        assert end_time - start_time < 5.0
        assert len(result.experience) == 20
        assert len(result.education) == 5

    def test_validation_integration_with_parsing(self):
        """Test validation integration throughout parsing pipeline."""
        # Test strict validation mode
        strict_parser = MarkdownResumeParser(strict_validation=True)
        
        # Resume that should fail strict validation
        weak_resume = """
# Test User
test@example.com

## Experience
### Intern
Company
- Did stuff

## Education  
### Degree
School
"""
        
        result, warnings = strict_parser.parse_with_warnings(weak_resume)
        
        # Should parse but have many warnings in strict mode
        assert len(warnings) > 0
        warning_text = " ".join(warnings).lower()
        assert "action verb" in warning_text or "sections" in warning_text

    def test_file_based_parsing(self):
        """Test parsing resume from file."""
        parser = MarkdownResumeParser()
        
        resume_content = """
# File Test User
file.test@example.com | (555) 123-4567

## Summary
Testing file-based resume parsing functionality.

## Experience
### Software Developer
TechCorp | 2022-Present
- Developed file processing applications
- Implemented automated testing pipelines
- Collaborated with QA team on test scenarios

## Education
### Computer Science Degree
Tech University | 2018-2022
- Focus on software engineering
- Capstone project on file systems

## Skills
- Python, Java, JavaScript
- File I/O, Testing, Git
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(resume_content)
            temp_filename = f.name
        
        try:
            # Read file and parse
            with open(temp_filename, 'r') as f:
                file_content = f.read()
            
            result = parser.parse(file_content)
            
            assert result.contact.name == "File Test User"
            assert result.contact.email == "file.test@example.com"
            assert len(result.experience) == 1
            assert len(result.education) == 1
            
        finally:
            # Clean up temporary file
            os.unlink(temp_filename)

    def test_concurrent_parsing(self):
        """Test concurrent parsing of multiple resumes."""
        import concurrent.futures
        import threading
        
        parser = MarkdownResumeParser(validate_input=False)
        
        def parse_resume(user_id):
            resume = f"""
# User {user_id}
user{user_id}@example.com

## Experience
### Developer {user_id}
Company {user_id}
- Built application {user_id}
- Worked on project {user_id}

## Education  
### Degree {user_id}
University {user_id}
"""
            return parser.parse(resume)
        
        # Test parsing multiple resumes concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(parse_resume, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All should parse successfully
        assert len(results) == 10
        for result in results:
            assert isinstance(result, ResumeData)
            assert result.contact.name.startswith("User ")

    def test_edge_case_handling(self):
        """Test handling of various edge cases."""
        parser = MarkdownResumeParser(validate_input=False)
        
        edge_cases = [
            # Unicode characters
            """
# José García
jose.garcia@email.com | +34 123 456 789

## Experiencia
### Desarrollador Senior
Empresa Española | 2020-Presente
- Desarrollé aplicaciones web
- Trabajé con equipos internacionales
""",
            
            # Very long content
            """
# Long Content User
long@example.com

## Experience
### Position with Very Long Title That Goes On and On and Describes Everything
Very Long Company Name That Includes Multiple Departments and Divisions
- """ + "Very long bullet point. " * 100,
            
            # Special characters in content
            """
# Special Chars User
special@example.com

## Experience
### C++ Developer & ML Engineer
Tech@Company | $100K salary | 50% remote
- Worked with C++, C#, .NET, & other technologies
- Improved performance by 25% (measured in ms/request)
- Led team of 5+ developers (junior & senior levels)
"""
        ]
        
        for i, edge_case in enumerate(edge_cases):
            try:
                result = parser.parse(edge_case)
                assert result.contact.name is not None
                # Should handle edge cases gracefully
            except Exception as e:
                pytest.fail(f"Edge case {i+1} failed: {e}")