def create_service_options():
    services = [
        "Web Design", "Application Development", "Digital Marketing", "Animation",
        "Branding", "Virtual Assistant", "Email Marketing", "Graphic Design",
        "Local SEO", "Advertising", "Logo Design", "Social Media Marketing", "SEO"
    ]
    return {service.lower().replace(" ", "_"): {
                "response": service,
                "next": {
                    "message": "Great! I will transfer you to my manager, who is an expert in this service.",
                }
            } for service in services}

def create_device_options():
    return {
        "computer": {
            "response": "I am on my computer.",
            "next": {
                "message": "At the top of the page, hover over the SERVICES button with your mouse. You will see a list of all our services.",
                "next": {
                    "message": "Please check out our services and let me know which one aligns with your needs.",
                    "options": create_service_options()
                },
            },
        },
        "phone": {
            "response": "I am on my phone.",
            "next": {
                "message": "Click the three horizontal lines at the top right corner of the page. You will see a list of all our services.",
                "next": {
                    "message": "Please check out our services and let me know which one aligns with your needs.",
                    "options": create_service_options()
                },
            },
        },
    }

def create_industry_response():
    return {
        "message": "Perfect, are you near your computer or phone?",
        "options": create_device_options()
    }

def create_project_response():
    return {
        "yes": {
            "response": "Yes, there is a project.",
            "next": {
                "message": "What industry is this for?",
                "next": create_industry_response()
            },
        },
        "no": {
            "response": "No, I just purchased it for future use.",
            "next": {
                "message": "Sometimes businesses plan for future projects. What industry is this for?",
                "next": create_industry_response()
            },
        },
    }

tree = {
    "message": "Hi [LEAD'S NAME], this is [MARC]. How are you?",
    "options": {
        "good": {
            "response": "Positive response",
            "next": {
                "message": "You recently purchased [LEAD'S WEBSITE]. Is there a project behind this?",
                "options": create_project_response()
            },
        },
        "not_good": {
            "response": "Negative response",
            "next": {
                "message": "I am sorry to hear that. You recently purchased [LEAD'S WEBSITE]. Is there a project behind this?",
                "options": create_project_response()
            },
        },
        "who_are_you": {
            "response": "Who are you?",
            "next": {
                "message": "I am calling from a high-performance marketing agency in New York that specializes in web design, mobile app development, and other business services. What industry is this for?",
                "options": create_project_response()
            },
        },
        "what_do_you_want": {
            "response": "What do you want?",
            "next": {
                "message": "I am calling from a high-performance marketing agency in New York that specializes in web design, mobile app development, and other business services. What industry is this for?",
                "options": create_project_response()
            },
        },
        "not_interested": {
            "response": "I'm not interested.",
            "next": {
                "message": "There is no way that your business is fully automated. Do you have a quick 30 seconds to check out our website to see if we can help your business with anything?",
                "options": create_project_response()
            },
        },
        "dont_have_time": {
            "response": "I don't have time.",
            "next": {
                "message": "I appreciate that. Can we schedule a follow-up call?",
                "options": create_project_response()
            },
        },
        "too_expensive": {
            "response": "It's too expensive.",
            "next": {
                "message": "We offer flexible pricing options. Can I explain them to you?",
                "options": create_project_response()
            },
        },
        "need_to_think": {
            "response": "I need to think about it.",
            "next": {
                "message": "I understand. What concerns do you have that I can address?",
                "options": create_project_response()
            },
        },
        "send_info": {
            "response": "Send me more information.",
            "next": {
                "message": "Sure, I can send you more information. What's the best email to reach you?",
                "options": create_project_response()
            },
        },
        "why_calling": {
            "response": "Why are you calling me?",
            "next": {
                "message": "We noticed that you recently purchased '[LEAD’S WEBSITE]'. Our goal is to see if we can help your business with anything.",
                "options": create_project_response()
            },
        },
        "other_projects": {
            "response": "I'm working on other projects.",
            "next": {
                "message": "What projects are you working on currently? Do you have a quick 30 seconds to check out our website?",
                "options": create_project_response()
            },
        },
        "dont_own_business": {
            "response": "I don't own a business.",
            "next": {
                "message": "That is unfortunate. However, do you have a quick 30 seconds to check out our website to see if we can help your current business with anything?",
                "options": create_project_response()
            },
        },
        "what_do_you_do": {
            "response": "What do you do?",
            "next": {
                "message": "We are experts in online marketing, web design, and mobile app development. Let me know once you have finished the video.",
                "options": create_project_response()
            },
        },
    },
}