import uuid

# 1. Mock Database of Content with Tags/Embeddings
MOVIE_DATABASE = [
    {"id": 101, "title": "Stranger Things", "tags": {"sci-fi", "thriller", "nostalgia"}},
    {"id": 102, "title": "Squid Game", "tags": {"thriller", "drama", "survival"}},
    {"id": 103, "title": "Our Planet", "tags": {"documentary", "nature", "relaxing"}},
    {"id": 104, "title": "The Crown", "tags": {"drama", "history", "royal"}},
    {"id": 105, "title": "Formula 1: Drive to Survive", "tags": {"sports", "action", "documentary"}},
    {"id": 106, "title": "Wednesday", "tags": {"fantasy", "mystery", "comedy"}},
]

# 2. Regional Fallback Data (If user rejects everything)
REGIONAL_TOP_10 = [101, 102, 105]

class NetflixUserConsentOnboarding:
    def __init__(self, email: str, base_subscription_fee: float = 649.0):
        self.user_id = str(uuid.uuid4())[:8]
        self.email = email
        self.base_fee = base_subscription_fee
        self.is_email_verified = False
        self.data_consent_granted = False
        self.applied_discount = 0.0
        self.user_tastes = set()

    def verify_email_and_prompt_consent(self, entered_otp: str, mock_otp: str, user_choice_consent: bool, initial_interests: list = None):
        """
        Simulates live email verification and captures explicit user data consent.
        Applies a strategic discount if consent is granted to maximize opt-in rates.
        """
        # Step A: Validate Email OTP
        if entered_otp != mock_otp:
            return {"status": "Error", "message": "Invalid OTP. Email verification failed."}
        
        self.is_email_verified = True
        
        # Step B: Evaluate Consent Choice & Apply Strategic Discount
        if user_choice_consent:
            self.data_consent_granted = True
            self.applied_discount = 0.20  # 20% promotional discount
            final_bill = self.base_fee * (1 - self.applied_discount)
            
            # Capture explicitly consented onboarding preferences to kill cold-start
            if initial_interests:
                self.user_tastes = set(initial_interests)
                
            msg = f"Success! Email verified. Consent granted. 20% discount applied. Final Bill: ₹{final_bill:.2f}"
        else:
            self.data_consent_granted = False
            self.applied_discount = 0.0
            final_bill = self.base_fee
            msg = f"Email verified. Consent denied. No discount applied. Final Bill: ₹{final_bill:.2f}"

        return {
            "status": "Success",
            "user_id": self.user_id,
            "message": msg,
            "consent": self.data_consent_granted,
            "final_bill": final_bill
        }

    def generate_homepage_feed(self):
        """
        Recommendation Engine Fallback Logic: Handles Cold Start state natively.
        """
        if not self.is_email_verified:
            return ["Please verify your email to access Netflix."]

        recommendations = []

        # Path A: Content-Based Filtering via Consented Tastes (Warm Start)
        if self.data_consent_granted and self.user_tastes:
            for movie in MOVIE_DATABASE:
                # Check overlapping interest tags
                if movie["tags"].intersection(self.user_tastes):
                    recommendations.append(movie["title"])
            
            # Fill remaining slots with regional trends if profile recommendations are low
            if len(recommendations) < 3:
                for mid in REGIONAL_TOP_10:
                    title = next(m["title"] for m in MOVIE_DATABASE if m["id"] == mid)
                    if title not in recommendations:
                        recommendations.append(title)
            return f"Personalized Feed for {self.email} (Based on explicit consent): {recommendations}"
        
        # Path B: Strict Privacy Fallback (Pure Cold Start due to Cookie/Data Rejection)
        else:
            for mid in REGIONAL_TOP_10:
                title = next(m["title"] for m in MOVIE_DATABASE if m["id"] == mid)
                recommendations.append(title)
            return f"Privacy-Safe Popular Feed (Zero user data used): {recommendations}"


# ==========================================
# EXECUTING SCENARIOS (CROSS-CHECK TESTING)
# ==========================================

print("--- SCENARIO 1: User Agrees to Email Consent for a Discount ---")
user1 = NetflixUserConsentOnboarding(email="rahul@example.com")
onboarding_result1 = user1.verify_email_and_prompt_consent(
    entered_otp="4582", 
    mock_otp="4582", 
    user_choice_consent=True, 
    initial_interests=["thriller", "sports"]
)
print(onboarding_result1["message"])
print(user1.generate_homepage_feed())
print("\n")

print("--- SCENARIO 2: User Verifies Email but Rejects Data Tracking (No Discount) ---")
user2 = NetflixUserConsentOnboarding(email="priya@example.com")
onboarding_result2 = user2.verify_email_and_prompt_consent(
    entered_otp="9911", 
    mock_otp="9911", 
    user_choice_consent=False
)
print(onboarding_result2["message"])
print(user2.generate_homepage_feed())
