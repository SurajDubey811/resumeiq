from typing import Dict, List, Set, Tuple
import re

# ----------------- CONFIGURABLE WEIGHTS -----------------

JOB_MATCHED_WEIGHTS = {
    "skills_alignment": 30.0,
    "relevant_experience": 25.0,
    "education_qualifications": 15.0,
    "measurable_achievements": 10.0,
    "resume_structure": 10.0,
    "ats_readability": 10.0,
}

RESUME_ONLY_WEIGHTS = {
    "skills_alignment": 20.0,
    "relevant_experience": 25.0,
    "education_qualifications": 15.0,
    "measurable_achievements": 20.0,
    "resume_structure": 10.0,
    "ats_readability": 10.0,
}

# Thresholds for tiers
SCORE_TIERS = [
    (85, "Strong"),
    (70, "Good"),
    (50, "Fair"),
    (0, "Needs Improvement"),
]


# ----------------- SYNONYM & SKILL DICTIONARY -----------------

SKILL_SYNONYMS: Dict[str, Set[str]] = {
    "python": {"python", "python3", "py"},
    "javascript": {"javascript", "js", "ecmascript", "es6", "es6+"},
    "typescript": {"typescript", "ts"},
    "react": {"react", "react.js", "reactjs", "react-native"},
    "node": {"node", "node.js", "nodejs"},
    "go": {"go", "golang"},
    "c++": {"c++", "cpp"},
    "c#": {"c#", "csharp", ".net", "dotnet"},
    "java": {"java", "jvm"},
    "ruby": {"ruby", "ruby on rails", "rails"},
    "php": {"php", "laravel"},
    "rust": {"rust", "rustlang"},
    "sql": {"sql", "rdbms", "relational database"},
    "postgresql": {"postgresql", "postgres", "psql"},
    "mysql": {"mysql", "mariadb"},
    "mongodb": {"mongodb", "mongo", "nosql"},
    "redis": {"redis", "in-memory cache"},
    "aws": {"aws", "amazon web services", "ec2", "s3", "lambda", "cloudformation"},
    "azure": {"azure", "microsoft azure"},
    "gcp": {"gcp", "google cloud", "google cloud platform", "bigquery"},
    "docker": {"docker", "containerization", "containers"},
    "kubernetes": {"kubernetes", "k8s"},
    "ci/cd": {"ci/cd", "ci-cd", "continuous integration", "continuous deployment", "jenkins", "github actions", "gitlab ci"},
    "git": {"git", "github", "gitlab", "version control"},
    "rest": {"rest", "restful", "rest api", "restful apis", "rest apis"},
    "graphql": {"graphql", "gql"},
    "fastapi": {"fastapi", "starlette"},
    "django": {"django", "django rest framework", "drf"},
    "flask": {"flask"},
    "express": {"express", "express.js", "expressjs"},
    "vue": {"vue", "vue.js", "vuejs"},
    "angular": {"angular", "angular.js", "angularjs"},
    "next.js": {"next.js", "nextjs", "next"},
    "tailwind": {"tailwind", "tailwindcss", "tailwind css"},
    "css": {"css", "css3", "sass", "scss", "less"},
    "html": {"html", "html5"},
    "linux": {"linux", "unix", "bash", "shell scripting", "posix"},
    "terraform": {"terraform", "iac", "infrastructure as code"},
    "ansible": {"ansible"},
    "kafka": {"kafka", "apache kafka", "event-driven architecture", "message queue"},
    "rabbitmq": {"rabbitmq", "amqp", "message broker"},
    "machine learning": {"machine learning", "ml", "deep learning", "neural networks"},
    "nlp": {"nlp", "natural language processing", "llm", "large language models", "rag", "transformers"},
    "pytorch": {"pytorch", "torch"},
    "tensorflow": {"tensorflow", "tf", "keras"},
    "scikit-learn": {"scikit-learn", "sklearn"},
    "data science": {"data science", "data analysis", "pandas", "numpy"},
    "microservices": {"microservices", "distributed systems", "service-oriented architecture"},
    "agile": {"agile", "scrum", "kanban", "sprints"},
    "unit testing": {"unit testing", "tdd", "test-driven development", "pytest", "jest", "mocking"},
    "graphql": {"graphql", "gql"},
    "system design": {"system design", "software architecture", "scalability", "high availability"},
    "security": {"cybersecurity", "security", "oauth", "jwt", "saml", "authentication", "authorization", "owasp"},
}

# Broad catalog of known technical & professional skills for auto-discovery
COMMON_TECH_SKILLS = set(SKILL_SYNONYMS.keys()) | {
    "api", "backend", "frontend", "full stack", "fullstack", "devops", "cloud",
    "etl", "data engineering", "spark", "hadoop", "airflow", "snowflake", "databricks",
    "monitoring", "prometheus", "grafana", "datadog", "new relic", "splunk",
    "elasticsearch", "solr", "opensearch", "dynamodb", "cassandra",
    "cypress", "playwright", "selenium", "postman",
    "webpack", "vite", "babel", "esbuild",
    "performance optimization", "caching", "cdn",
    "leadership", "mentorship", "cross-functional collaboration", "project management",
    "code review", "debugging", "ci", "cd"
}

# Action verbs strongly associated with high-impact resumes
ACTION_VERBS = {
    "architected", "spearheaded", "engineered", "designed", "implemented", "developed",
    "optimized", "accelerated", "scaled", "reduced", "increased", "decreased", "improved",
    "streamlined", "automated", "mentored", "led", "managed", "delivered", "deployed",
    "launched", "revamped", "eliminated", "boosted", "maximized", "transformed", "pioneered",
    "orchestrated", "negotiated", "resolved", "generated", "saved", "built", "drove"
}

# Degree level hierarchy
DEGREE_LEVELS = {
    "doctorate": 5,
    "phd": 5,
    "ph.d": 5,
    "master": 4,
    "masters": 4,
    "m.s": 4,
    "ms": 4,
    "m.a": 4,
    "mba": 4,
    "bachelor": 3,
    "bachelors": 3,
    "b.s": 3,
    "bs": 3,
    "b.a": 3,
    "ba": 3,
    "b.tech": 3,
    "btech": 3,
    "b.e": 3,
    "be": 3,
    "associate": 2,
    "associates": 2,
    "high school": 1,
    "diploma": 1,
}
