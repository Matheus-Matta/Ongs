from django.http import JsonResponse
from django.contrib.auth.decorators import login_required 
from django.utils.timezone import now
from django.contrib import messages
from account.models import Post, Event, ImagePost, Volunteer, User, Comment
from datetime import datetime
from django.core.paginator import Paginator , EmptyPage
from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404 , redirect
from datetime import date
from django.db.models import Prefetch
import json
import re


@login_required
def chat_list(request):
    return render(request, "apps/social/chat.html")