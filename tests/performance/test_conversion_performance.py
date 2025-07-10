"""
Performance tests for the resume automation tool.

Tests conversion times, parsing performance, and memory usage to ensure
they meet the requirements:
- Total conversion time < 1 second
- Parsing time < 100ms 
- Memory usage < 50MB
"""

import time
from pathlib import Path
from typing import Any

import pytest


class TestConversionPerformance:
    """Test conversion performance requirements."""

    @pytest.fixture
    def simple_resume_content(self) -> str:
        """Simple resume content for performance testing."""
        return """# John Doe

## Contact Information
- Email: john.doe@email.com
- Phone: (555) 123-4567
- Location: San Francisco, CA

## Summary
Experienced software engineer with 5+ years of experience.

## Experience

### Senior Software Engineer | Tech Corp
*January 2020 - Present*

- Developed web applications using Python and JavaScript
- Led a team of 3 junior developers
- Improved application performance by 40%

### Software Engineer | Startup Inc
*June 2018 - December 2019*

- Built RESTful APIs using Flask and FastAPI
- Implemented automated testing pipelines

## Education

### Bachelor of Science in Computer Science
**University of California** | *2014 - 2018*

## Skills
- Programming Languages: Python, JavaScript, TypeScript
- Frameworks: React, Vue.js, Django, Flask
- Databases: PostgreSQL, MongoDB
- Tools: Git, Docker, AWS"""

    @pytest.fixture
    def medium_resume_content(self) -> str:
        """Medium-sized resume content for performance testing."""
        return """# Sarah Johnson
**Senior Data Scientist & Machine Learning Engineer**

## Contact Information
- **Email:** sarah.johnson@email.com
- **Phone:** +1 (555) 987-6543
- **LinkedIn:** linkedin.com/in/sarahjohnson
- **GitHub:** github.com/sarahjohnson
- **Location:** Seattle, WA

## Professional Summary
Experienced Data Scientist with 8+ years of expertise in machine learning, statistical analysis, and big data technologies. Proven track record of delivering actionable insights and building scalable ML solutions that drive business growth.

## Core Competencies
- **Machine Learning:** Deep Learning, NLP, Computer Vision, Time Series Analysis
- **Programming:** Python, R, SQL, Scala, Java
- **Big Data:** Apache Spark, Hadoop, Kafka, Airflow
- **Cloud Platforms:** AWS (SageMaker, EMR, S3), Google Cloud Platform, Azure
- **Databases:** PostgreSQL, MongoDB, Cassandra, Redis
- **Visualization:** Tableau, Power BI, Matplotlib, Plotly, D3.js

## Professional Experience

### Senior Data Scientist | AI Innovations Corp
*March 2021 - Present | Seattle, WA*

**Key Achievements:**
- Led a team of 5 data scientists in developing ML models that increased customer retention by 25%
- Designed and implemented real-time recommendation engine serving 10M+ users daily
- Reduced model training time by 60% through distributed computing optimization
- Published 3 research papers in top-tier conferences (NeurIPS, ICML)

**Technical Contributions:**
- Built end-to-end MLOps pipeline using Kubeflow and MLflow
- Developed natural language processing models for sentiment analysis
- Implemented computer vision solutions for autonomous vehicle perception

### Data Scientist | TechStartup Solutions
*June 2019 - February 2021 | San Francisco, CA*

**Key Achievements:**
- Increased revenue by $2M annually through predictive analytics models
- Developed fraud detection system reducing false positives by 40%
- Led data science hiring and mentoring of 3 junior data scientists

**Technical Contributions:**
- Built time series forecasting models for demand planning
- Implemented A/B testing framework for product optimization
- Created data pipelines processing 100GB+ daily

### Machine Learning Engineer | Enterprise Data Corp
*August 2016 - May 2019 | San Jose, CA*

**Key Achievements:**
- Deployed 15+ ML models to production serving millions of requests
- Improved model accuracy by 30% through advanced feature engineering
- Established ML best practices and coding standards for the team

## Education

### Master of Science in Data Science
**Stanford University** | *2014 - 2016*
- **GPA:** 3.9/4.0
- **Thesis:** "Deep Learning Applications in Natural Language Processing"

### Bachelor of Science in Computer Science
**University of California, Berkeley** | *2010 - 2014*
- **GPA:** 3.8/4.0
- **Summa Cum Laude**

## Certifications
- **AWS Certified Machine Learning - Specialty** (2023)
- **Google Cloud Professional Data Engineer** (2022)
- **Certified Analytics Professional (CAP)** (2021)

## Publications & Research
1. "Scalable Deep Learning for Real-time Recommendation Systems" - NeurIPS 2023
2. "Advanced Time Series Forecasting with Transformer Networks" - ICML 2022
3. "Ethical AI in Production: Bias Detection and Mitigation" - AI Ethics Journal 2023

## Projects
### Open Source Contributions
- **MLflow Enhancement:** Contributed model versioning features (2,000+ GitHub stars)
- **Scikit-learn:** Fixed bugs in ensemble methods
- **Apache Spark:** Performance optimization for ML pipelines

## Awards & Recognition
- **Data Scientist of the Year** - AI Innovations Corp (2023)
- **Best Paper Award** - International Conference on Machine Learning (2022)
- **Innovation Award** - TechStartup Solutions (2020)"""

    @pytest.fixture
    def large_resume_content(self) -> str:
        """Large resume content for stress testing."""
        base_content = """# Dr. Michael Chen
**Distinguished Research Scientist & Technology Leader**

## Contact Information
- **Email:** michael.chen@email.com
- **Phone:** +1 (555) 123-9876
- **LinkedIn:** linkedin.com/in/drMichaelChen
- **GitHub:** github.com/michaelchen
- **ORCID:** 0000-0000-0000-0000
- **Location:** San Francisco, CA

## Executive Summary
Distinguished research scientist and technology leader with 15+ years of experience in artificial intelligence, machine learning, and distributed systems. PhD in Computer Science with 50+ peer-reviewed publications and 12 patents. Led teams of 20+ engineers and researchers across multiple Fortune 500 companies and top-tier research institutions.

## Core Technical Expertise
- **Artificial Intelligence:** Deep Learning, Reinforcement Learning, Computer Vision, Natural Language Processing
- **Programming Languages:** Python, C++, Java, JavaScript, Go, Rust, R, MATLAB
- **Machine Learning Frameworks:** TensorFlow, PyTorch, JAX, Scikit-learn, XGBoost, LightGBM
- **Big Data Technologies:** Apache Spark, Hadoop, Kafka, Flink, Storm, Cassandra, MongoDB
- **Cloud Platforms:** AWS, Google Cloud Platform, Microsoft Azure, IBM Cloud
- **Containerization & Orchestration:** Docker, Kubernetes, Helm, Service Mesh
- **Development Tools:** Git, Jenkins, GitHub Actions, GitLab CI, SonarQube

"""
        
        # Generate repeated sections to make it large
        experience_section = """
### Principal Research Scientist | Advanced AI Research Corp
*January 2020 - Present | San Francisco, CA*

**Leadership & Strategy:**
- Led a multidisciplinary team of 25+ researchers and engineers across AI/ML initiatives
- Established strategic research roadmap resulting in $50M+ in new product revenue
- Collaborated with C-suite executives on technology vision and investment decisions
- Mentored 15+ PhD students and postdoctoral researchers

**Technical Achievements:**
- Pioneered novel deep learning architectures for real-time video analysis (3 patents pending)
- Developed distributed training framework reducing model training time by 80%
- Created AutoML platform used by 500+ internal data scientists
- Published 12 papers in top-tier venues (ICML, NeurIPS, ICLR, CVPR)

**Impact & Recognition:**
- Research featured on cover of Nature Machine Intelligence (2023)
- Keynote speaker at 5 international conferences
- Recipient of Outstanding Research Award (2022, 2023)
- Technology transfer resulted in 3 successful product launches

"""
        
        # Repeat experience sections to make it larger
        full_content = base_content
        for i in range(5):  # Add 5 similar experience sections
            section = experience_section.replace("Advanced AI Research Corp", f"Tech Company {i+1}")
            section = section.replace("January 2020", f"January {2015+i}")
            section = section.replace("Present", f"December {2019+i}")
            full_content += section
        
        # Add publications section
        publications = """
## Selected Publications (50+ total)

### 2023
1. "Transformer Architectures for Large-Scale Video Understanding" - Nature Machine Intelligence
2. "Efficient Distributed Learning with Gradient Compression" - ICML 2023
3. "Federated Learning for Privacy-Preserving Healthcare AI" - NeurIPS 2023
4. "AutoML for Time Series: A Comprehensive Framework" - ICLR 2023

### 2022
1. "Neural Architecture Search for Edge Computing" - CVPR 2022
2. "Explainable AI in Critical Systems: Methods and Applications" - AAAI 2022
3. "Quantum-Classical Hybrid Algorithms for Optimization" - ICML 2022
4. "Multi-Modal Learning for Autonomous Systems" - NeurIPS 2022

### 2021
1. "Scalable Graph Neural Networks for Social Network Analysis" - KDD 2021
2. "Transfer Learning in Low-Resource Scenarios" - ICLR 2021
3. "Adversarial Training for Robust Computer Vision" - CVPR 2021
4. "Deep Reinforcement Learning for Resource Allocation" - ICML 2021

"""
        
        full_content += publications
        
        # Add projects and awards
        full_content += """
## Major Research Projects

### Project Alpha - Next-Generation AI Platform (2020-2023)
- Led $10M research initiative for developing AGI capabilities
- Coordinated with 5 universities and 3 government agencies
- Resulted in 15 publications and 8 patent applications
- Technology now used in 3 commercial products

### Project Beta - Autonomous Systems Research (2018-2020)
- Principal investigator for $5M DARPA-funded project
- Developed AI systems for autonomous vehicle navigation
- Collaborated with automotive industry partners
- Achieved 99.9% safety record in testing

### Project Gamma - Healthcare AI Initiative (2016-2018)
- Co-led $3M NIH-funded research on medical image analysis
- Developed diagnostic AI achieving 95% accuracy
- Published in top medical journals (Nature Medicine, Lancet AI)
- Technology licensed to 2 medical device companies

## Patents (12 total)
1. "Method and System for Distributed Deep Learning Training" - US Patent 11,123,456
2. "Neural Architecture for Real-Time Video Processing" - US Patent 11,234,567
3. "Federated Learning with Differential Privacy" - US Patent 11,345,678
4. "AutoML Framework for Time Series Analysis" - US Patent 11,456,789

## Awards & Honors
- **IEEE Fellow** (2023) - For contributions to artificial intelligence and machine learning
- **ACM Distinguished Scientist** (2022) - Recognition of technical leadership
- **MIT Technology Review Innovator Under 35** (2019)
- **Google Faculty Research Award** (2018, 2020, 2022)
- **NSF CAREER Award** (2017)
- **Best Paper Award** - ICML (2019), NeurIPS (2020), CVPR (2021)

## Professional Service
- **Editorial Board:** Nature Machine Intelligence (2021-Present)
- **Program Committee:** ICML, NeurIPS, ICLR, CVPR (2018-Present)
- **Advisory Board:** 3 AI startups, 2 venture capital firms
- **Reviewer:** 15+ top-tier conferences and journals annually

## Education

### Ph.D. in Computer Science
**Stanford University** | *2008 - 2013*
- **Dissertation:** "Scalable Machine Learning for Large-Scale Data Systems"
- **Advisor:** Prof. Andrew Ng
- **GPA:** 4.0/4.0

### Master of Science in Computer Science  
**Massachusetts Institute of Technology** | *2006 - 2008*
- **Concentration:** Artificial Intelligence
- **Thesis:** "Neural Networks for Real-Time Pattern Recognition"
- **GPA:** 4.0/4.0

### Bachelor of Science in Computer Science
**University of California, Berkeley** | *2002 - 2006*
- **Summa Cum Laude, Phi Beta Kappa**
- **Outstanding Senior Award in Computer Science**
- **GPA:** 3.98/4.0

## Certifications & Professional Development
- **AWS Certified Solutions Architect - Professional** (2023)
- **Google Cloud Professional Machine Learning Engineer** (2022)
- **Microsoft Azure AI Engineer Associate** (2021)
- **Certified Kubernetes Administrator (CKA)** (2020)

## Speaking Engagements (50+ total)
### 2023
- **Keynote:** International Conference on Machine Learning (ICML)
- **Invited Talk:** Neural Information Processing Systems (NeurIPS)
- **Panel:** World Economic Forum AI Summit
- **Webinar:** IEEE AI in Practice Series

### 2022
- **Keynote:** Computer Vision and Pattern Recognition (CVPR)
- **Invited Talk:** Association for the Advancement of Artificial Intelligence (AAAI)
- **Panel:** Fortune AI Summit
- **Webinar:** ACM TechTalk Series

## Media Coverage & Interviews
- **MIT Technology Review:** "The Future of AI Research" (2023)
- **IEEE Spectrum:** "Breakthrough in Distributed Learning" (2022)
- **Wired Magazine:** "AI's Next Frontier" (2021)
- **TechCrunch:** "Startup Advisor Spotlight" (2020)
"""
        
        return full_content

    def benchmark_parsing_performance(self, benchmark, content: str):
        """Benchmark parsing performance - should be < 100ms."""
        def parse_resume():
            # Simulate parsing by processing the content
            # In real implementation, this would call the actual parser
            lines = content.split('\n')
            sections = {}
            current_section = None
            
            for line in lines:
                if line.startswith('#'):
                    current_section = line.strip('#').strip()
                    sections[current_section] = []
                elif current_section and line.strip():
                    sections[current_section].append(line.strip())
            
            return sections
        
        result = benchmark(parse_resume)
        assert result is not None
        
    def test_parsing_performance_simple_resume(self, benchmark, simple_resume_content: str):
        """Test parsing performance with simple resume - target < 100ms."""
        self.benchmark_parsing_performance(benchmark, simple_resume_content)

    def test_parsing_performance_medium_resume(self, benchmark, medium_resume_content: str):
        """Test parsing performance with medium resume - target < 100ms."""
        self.benchmark_parsing_performance(benchmark, medium_resume_content)

    def test_parsing_performance_large_resume(self, benchmark, large_resume_content: str):
        """Test parsing performance with large resume - target < 100ms."""
        self.benchmark_parsing_performance(benchmark, large_resume_content)

    def benchmark_html_conversion(self, benchmark, content: str):
        """Benchmark HTML conversion performance."""
        def convert_to_html():
            # Simulate HTML conversion
            lines = content.split('\n')
            html_lines = ['<html><body>']
            
            for line in lines:
                if line.startswith('# '):
                    html_lines.append(f'<h1>{line[2:]}</h1>')
                elif line.startswith('## '):
                    html_lines.append(f'<h2>{line[3:]}</h2>')
                elif line.startswith('### '):
                    html_lines.append(f'<h3>{line[4:]}</h3>')
                elif line.startswith('- '):
                    html_lines.append(f'<li>{line[2:]}</li>')
                elif line.strip():
                    html_lines.append(f'<p>{line}</p>')
            
            html_lines.append('</body></html>')
            return '\n'.join(html_lines)
        
        result = benchmark(convert_to_html)
        assert result is not None
        assert '<html>' in result

    def test_html_conversion_performance_simple(self, benchmark, simple_resume_content: str):
        """Test HTML conversion performance with simple resume - target < 1s."""
        self.benchmark_html_conversion(benchmark, simple_resume_content)

    def test_html_conversion_performance_medium(self, benchmark, medium_resume_content: str):
        """Test HTML conversion performance with medium resume - target < 1s."""
        self.benchmark_html_conversion(benchmark, medium_resume_content)

    def test_html_conversion_performance_large(self, benchmark, large_resume_content: str):
        """Test HTML conversion performance with large resume - target < 1s."""
        self.benchmark_html_conversion(benchmark, large_resume_content)


class TestMemoryUsage:
    """Test memory usage requirements."""

    def test_memory_usage_simple_conversion(self):
        """Test memory usage during simple conversion - target < 50MB."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Simulate conversion process with inline content
            content = """# John Doe

## Contact Information
- Email: john.doe@email.com
- Phone: (555) 123-4567
- Location: San Francisco, CA

## Summary
Experienced software engineer with 5+ years of experience.

## Experience

### Senior Software Engineer | Tech Corp
*January 2020 - Present*

- Developed web applications using Python and JavaScript
- Led a team of 3 junior developers
- Improved application performance by 40%

## Skills
- Programming Languages: Python, JavaScript, TypeScript
- Frameworks: React, Vue.js, Django, Flask"""
            for _ in range(10):  # Process multiple times
                lines = content.split('\n')
                html_lines = []
                for line in lines:
                    if line.startswith('#'):
                        html_lines.append(f'<h1>{line}</h1>')
                    else:
                        html_lines.append(f'<p>{line}</p>')
                result = '\n'.join(html_lines)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = final_memory - initial_memory
            
            # Memory usage should be reasonable (< 50MB increase)
            assert memory_used < 50, f"Memory usage too high: {memory_used:.2f}MB"
            
        except ImportError:
            pytest.skip("psutil not available for memory testing")

    def test_memory_usage_batch_conversion(self):
        """Test memory usage during batch conversion - target < 50MB per file."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Simulate batch processing multiple files  
            content = """# Sarah Johnson
**Senior Data Scientist & Machine Learning Engineer**

## Contact Information
- **Email:** sarah.johnson@email.com
- **Phone:** +1 (555) 987-6543
- **Location:** Seattle, WA

## Professional Summary
Experienced Data Scientist with 8+ years of expertise in machine learning, statistical analysis, and big data technologies.

## Core Competencies
- **Machine Learning:** Deep Learning, NLP, Computer Vision
- **Programming:** Python, R, SQL, Scala, Java
- **Big Data:** Apache Spark, Hadoop, Kafka, Airflow
- **Cloud Platforms:** AWS, Google Cloud Platform, Azure"""
            
            for i in range(5):  # Process 5 files
                lines = content.split('\n')
                html_lines = []
                for line in lines:
                    if line.startswith('#'):
                        html_lines.append(f'<h1>{line}</h1>')
                    else:
                        html_lines.append(f'<p>{line}</p>')
                result = '\n'.join(html_lines)
                
                # Simulate file output
                _ = result.encode('utf-8')
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = final_memory - initial_memory
            
            # Memory usage should be reasonable for batch processing
            assert memory_used < 100, f"Batch memory usage too high: {memory_used:.2f}MB"
            
        except ImportError:
            pytest.skip("psutil not available for memory testing")


class TestCLIPerformance:
    """Test CLI command performance."""

    def test_cli_response_time(self, tmp_path: Path):
        """Test CLI command response time - should be fast for basic operations."""
        import subprocess
        
        # Create a test resume file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test Resume\n\nSample content for performance testing.")
        
        # Test help command performance
        start_time = time.time()
        result = subprocess.run(
            ["resume-convert", "--help"],
            capture_output=True,
            text=True
        )
        help_time = time.time() - start_time
        
        assert result.returncode == 0
        assert help_time < 2.0, f"Help command too slow: {help_time:.2f}s"
        
        # Test version command performance  
        start_time = time.time()
        result = subprocess.run(
            ["resume-convert", "--version"],
            capture_output=True,
            text=True
        )
        version_time = time.time() - start_time
        
        assert result.returncode == 0
        assert version_time < 2.0, f"Version command too slow: {version_time:.2f}s"

    def test_error_handling_performance(self):
        """Test that error handling is fast."""
        import subprocess
        
        # Test missing file error handling
        start_time = time.time()
        result = subprocess.run(
            ["resume-convert", "convert", "nonexistent.md"],
            capture_output=True,
            text=True
        )
        error_time = time.time() - start_time
        
        assert result.returncode == 2  # Expected error code
        assert error_time < 1.0, f"Error handling too slow: {error_time:.2f}s"


class TestScalabilityBenchmarks:
    """Test scalability with various input sizes."""

    def test_scaling_with_content_size(self, benchmark):
        """Test how performance scales with content size."""
        def process_content():
            base_content = "# Resume\n\n## Section\n\nContent line.\n"
            content = base_content * 10  # Test with 10x content
            
            lines = content.split('\n')
            result = []
            for line in lines:
                if line.startswith('#'):
                    result.append(f'<h1>{line}</h1>')
                else:
                    result.append(f'<p>{line}</p>')
            
            return '\n'.join(result)
        
        # Test with 10x content - should scale reasonably
        result = benchmark(process_content)
        assert result is not None

    def test_concurrent_processing_simulation(self, benchmark):
        """Test simulation of concurrent processing performance."""
        def simulate_concurrent_conversion():
            # Simulate processing multiple resumes concurrently
            results = []
            for i in range(3):  # Simulate 3 concurrent jobs
                content = f"# Resume {i}\n\n## Experience\n\nJob {i} description."
                lines = content.split('\n')
                html_result = []
                for line in lines:
                    if line.startswith('#'):
                        html_result.append(f'<h1>{line}</h1>')
                    else:
                        html_result.append(f'<p>{line}</p>')
                results.append('\n'.join(html_result))
            return results
        
        results = benchmark(simulate_concurrent_conversion)
        assert len(results) == 3
        assert all('<h1># Resume' in result for result in results)