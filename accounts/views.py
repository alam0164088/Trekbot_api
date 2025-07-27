from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import CustomUser, OTP
from .serializers import *
from .utils import generate_otp, send_otp_via_email

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Signup successful!'}, status=201)
        return Response(serializer.errors, status=400)

class SigninView(APIView):
    def post(self, request):
        serializer = SigninSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if user:
                return Response({'message': 'Signin successful!'}, status=200)
            return Response({'error': 'Invalid credentials'}, status=401)
        return Response(serializer.errors, status=400)

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                otp = generate_otp()
                OTP.objects.create(user=user, code=otp)
                send_otp_via_email(email, otp)
                return Response({'message': 'OTP sent to email'}, status=200)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)
        return Response(serializer.errors, status=400)

class OTPVerifyView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            try:
                user = CustomUser.objects.get(email=email)
                otp_obj = OTP.objects.filter(user=user, code=otp, is_used=False).last()
                if otp_obj:
                    return Response({'message': 'OTP verified'}, status=200)
                return Response({'error': 'Invalid or used OTP'}, status=400)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)
        return Response(serializer.errors, status=400)

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                OTP.objects.filter(user=user).update(is_used=True)  # Mark all as used
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({'message': 'Password reset successful!'}, status=200)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)
        return Response(serializer.errors, status=400)
