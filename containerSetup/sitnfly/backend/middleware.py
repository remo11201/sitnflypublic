# # backend/middleware.py

# from django.shortcuts import redirect
# from django.urls import reverse

# class TwoFactorAuthenticationMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if request.user.is_authenticated:
#             if not request.session.get('is_2fa_verified', False):
#                 # If the user is authenticated but 2FA is not verified, redirect to 2FA verification page
#                 if not request.path.startswith(reverse('verify_2fa_email')):
#                     return redirect('verify_2fa_email')
#         response = self.get_response(request)
#         return response
