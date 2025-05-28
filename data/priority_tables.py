# data/priority_tables.py

# Priority table for Software Developer
priority_table_developer = {
    'happy': {
        'brainstorm new features': 0.95,
        'code review sessions': 0.9,
        'architectural discussions': 0.88
    },
    'sad': {
        'bug fixing': 0.92,
        'documentation updates': 0.88,
        'unit testing': 0.85
    },
    'angry': {
        'work on isolated modules': 0.9,
        'backend optimization': 0.88,
        'refactoring old code': 0.86
    },
    'neutral': {
        'attend sprint planning': 0.88,
        'daily standup meetings': 0.85,
        'peer programming': 0.83
    },
    'fear': {
        'code walkthroughs with senior': 0.92,
        'mentored programming tasks': 0.9,
        'shadowing deployments': 0.87
    },
    'disgust': {
        'legacy code maintenance': 0.9,
        'code comment cleanup': 0.87,
        'bug tracking analysis': 0.85
    },
    'surprise': {
        'rapid prototyping': 0.95,
        'experimental feature building': 0.92,
        'spike tasks for research': 0.9
    }
}

# Priority table for DevOps Engineer
priority_table_devops = {
    'happy': {
        'design CI/CD workflows': 0.95,
        'optimize deployment pipelines': 0.9,
        'explore cloud automation': 0.88
    },
    'sad': {
        'server monitoring': 0.92,
        'backup script checks': 0.88,
        'routine security audits': 0.85
    },
    'angry': {
        'isolated infrastructure setup': 0.9,
        'server hardening tasks': 0.88,
        'container optimizations': 0.87
    },
    'neutral': {
        'handle change requests': 0.88,
        'prepare incident reports': 0.85,
        'system updates coordination': 0.83
    },
    'fear': {
        'work with senior DevOps on deployments': 0.92,
        'shadow cloud migration': 0.9,
        'supervised disaster recovery drill': 0.87
    },
    'disgust': {
        'review error logs': 0.9,
        'cleanup unused cloud resources': 0.87,
        'fix outdated scripts': 0.85
    },
    'surprise': {
        'test new DevOps tools': 0.95,
        'R&D on infrastructure as code': 0.92,
        'experiment with observability platforms': 0.9
    }
}

# Priority table for Product Designer
priority_table_designer = {
    'happy': {
        'create new UI designs': 0.95,
        'design brand concepts': 0.9,
        'storyboarding for user journey': 0.88
    },
    'sad': {
        'prepare design documentation': 0.92,
        'organize design assets': 0.88,
        'standardize design libraries': 0.85
    },
    'angry': {
        'work independently on low-pressure mockups': 0.9,
        'audit old designs for improvements': 0.88,
        'review usability test reports': 0.87
    },
    'neutral': {
        'attend UX workshops': 0.88,
        'client design feedback meetings': 0.85,
        'collaborate on feature design updates': 0.83
    },
    'fear': {
        'shadow senior designer sessions': 0.92,
        'participate in usability testing': 0.9,
        'mock client demos (internal)': 0.87
    },
    'disgust': {
        'cleanup outdated Figma files': 0.9,
        'archive old project assets': 0.87,
        'standard compliance reviews': 0.85
    },
    'surprise': {
        'hackathon on innovative UX ideas': 0.95,
        'rapid wireframing of new concepts': 0.92,
        'visual exploration of experimental styles': 0.9
    }
}


priority_tables = {
    "developer": priority_table_developer,
    "devops": priority_table_devops,
    "designer": priority_table_designer
}
