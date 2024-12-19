import uuid

def generate_referral_code(length=20):
    return f"INST-{uuid.uuid4().hex[:length].upper()}"


# from django.contrib.auth.tokens import PasswordResetTokenGenerator


# class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
#     def _make_hash_value(self, user, timestamp):
#         return (
#             str(user.is_active) + str(user.pk) + str(timestamp)
#         )


# email_verification_token = EmailVerificationTokenGenerator()
