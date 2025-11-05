"""
Example usage of Google Form Generator
Demonstrates various question types and form creation scenarios
"""

from google_form_generator import GoogleFormGenerator


def example_basic_form():
    """Create a basic form with common question types."""
    print("Creating basic form...")
    
    generator = GoogleFormGenerator()
    
    form = generator.create_form(
        title="Customer Feedback Survey",
        description="Please take a few minutes to share your feedback with us."
    )
    
    # Short answer text
    form.add_question(
        question_text="What is your name?",
        question_type="text",
        required=True
    )
    
    # Email address (using text type)
    form.add_question(
        question_text="What is your email address?",
        question_type="text",
        required=True
    )
    
    # Rating scale
    form.add_question(
        question_text="How satisfied are you with our service?",
        question_type="scale",
        scale_min=1,
        scale_max=5,
        scale_min_label="Very Dissatisfied",
        scale_max_label="Very Satisfied",
        required=True
    )
    
    # Multiple choice
    form.add_question(
        question_text="How did you hear about us?",
        question_type="choice",
        options=["Social Media", "Friend/Colleague", "Advertisement", "Search Engine", "Other"],
        required=True
    )
    
    # Checkbox (multiple selections)
    form.add_question(
        question_text="Which features do you use? (Select all that apply)",
        question_type="checkbox",
        options=["Feature A", "Feature B", "Feature C", "Feature D"]
    )
    
    # Dropdown
    form.add_question(
        question_text="What is your age range?",
        question_type="dropdown",
        options=["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
        required=True
    )
    
    # Paragraph text (long answer)
    form.add_question(
        question_text="Any additional comments or suggestions?",
        question_type="paragraph"
    )
    
    form_url = form.get_url()
    print(f"\n✅ Basic form created successfully!")
    print(f"View form: {form_url}")
    print(f"Edit form: {form.get_edit_url()}\n")
    
    return form_url


def example_event_registration_form():
    """Create an event registration form."""
    print("Creating event registration form...")
    
    generator = GoogleFormGenerator()
    
    form = generator.create_form(
        title="Event Registration Form",
        description="Register for our upcoming event"
    )
    
    form.add_question(
        question_text="Full Name",
        question_type="text",
        required=True
    )
    
    form.add_question(
        question_text="Email Address",
        question_type="text",
        required=True
    )
    
    form.add_question(
        question_text="Phone Number",
        question_type="text",
        required=True
    )
    
    form.add_question(
        question_text="Event Date",
        question_type="date",
        required=True
    )
    
    form.add_question(
        question_text="Preferred Time",
        question_type="time",
        required=True
    )
    
    form.add_question(
        question_text="Dietary Restrictions",
        question_type="checkbox",
        options=["Vegetarian", "Vegan", "Gluten-Free", "Nut Allergy", "None"]
    )
    
    form.add_question(
        question_text="Special Accommodations or Requests",
        question_type="paragraph"
    )
    
    form_url = form.get_url()
    print(f"\n✅ Event registration form created successfully!")
    print(f"View form: {form_url}")
    print(f"Edit form: {form.get_edit_url()}\n")
    
    return form_url


def example_feedback_form():
    """Create a product feedback form."""
    print("Creating product feedback form...")
    
    generator = GoogleFormGenerator()
    
    form = generator.create_form(
        title="Product Feedback",
        description="Help us improve our product by sharing your thoughts"
    )
    
    form.add_question(
        question_text="Product Name",
        question_type="text",
        required=True
    )
    
    form.add_question(
        question_text="Overall Rating",
        question_type="scale",
        scale_min=1,
        scale_max=10,
        scale_min_label="Poor",
        scale_max_label="Excellent",
        required=True
    )
    
    form.add_question(
        question_text="What do you like most about the product?",
        question_type="paragraph",
        required=True
    )
    
    form.add_question(
        question_text="What could be improved?",
        question_type="paragraph"
    )
    
    form.add_question(
        question_text="Would you recommend this product?",
        question_type="choice",
        options=["Yes", "No", "Maybe"],
        required=True
    )
    
    form.add_question(
        question_text="Category of feedback",
        question_type="dropdown",
        options=["Feature Request", "Bug Report", "Usability", "Performance", "Other"]
    )
    
    form_url = form.get_url()
    print(f"\n✅ Product feedback form created successfully!")
    print(f"View form: {form_url}")
    print(f"Edit form: {form.get_edit_url()}\n")
    
    return form_url


def main():
    """Run all examples."""
    print("=" * 60)
    print("Google Forms Generator - Example Usage")
    print("=" * 60)
    print()
    
    try:
        # Example 1: Basic form
        example_basic_form()
        
        # Example 2: Event registration
        example_event_registration_form()
        
        # Example 3: Feedback form
        example_feedback_form()
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease make sure you have:")
        print("1. Downloaded credentials.json from Google Cloud Console")
        print("2. Placed it in the project root directory")
        print("3. Enabled Google Forms API in your Google Cloud project")
        
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

