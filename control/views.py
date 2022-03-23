import email
from pickle import TRUE
from re import M
import re
from tkinter.tix import Tree
from turtle import title
from django import dispatch
from django.contrib.auth.models import Group, Permission, PermissionsMixin
from django.core.exceptions import ValidationError
from django.http import request
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404, render_to_response
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import View
from django.db.models import Q, Sum
import json
import string
import random
from control.models import *
from control.forms import *
import pendulum

class HomePageView(View):
    @method_decorator(never_cache)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self,request,*args, **kwargs):
        title = "Dashboard"
        user_type = request.user.profile.user_type
        if user_type == 1:
            posts = StudentPost.objects.filter(owner=request.user,is_active=True,is_deleted=False)
            sub_title = "My Post(s)"
        elif user_type == 2:
            sub_title = "Posts Related To you"
            tags = ','.join(request.user.profile.get_user_registered_tag())
            posts = StudentPost.objects.filter(is_active=True,is_deleted=False,tags__icontains=tags,owner__profile__location=request.user.profile.location)
        else:
            sub_title = "Post"
            posts = StudentPost.objects.all()
        context = {
            'posts': posts,
            'title': title,
            'sub_title': sub_title
        }
        return render(request,"home/home_page.html",context)


class LogInForm(View):
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    form_class = LogInForm
    template_name = 'home/login.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form,'title': 'Login'})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                if request.GET.get("next"):
                    return redirect(request.GET.get("next"))
                else:
                    return redirect('/')
            else:
                raise ValidationError('Wrong username or password')
        else:
            return render(request, self.template_name, {'form': form,'title': 'Login'})

def logout_view(request):
    logout(request)
    return redirect("login")

class UserRegistrationView(View):
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(Self,request,*args, **kwargs):
        form = UserProfileForm()
        title = "User Registration"
        context = {
            'form': form,
            'title': title
        }
        return render(request,"home/user_registration.html",context)
    
    def post(self,request,*args, **kwargs):
        title = "User Registration"
        form = UserProfileForm(request.POST)

        if form.is_valid():
            full_name = str(form.cleaned_data.get("full_name")).split(' ')
            middle_name = ''
            first_name = ''
            last_name = ''
            location = Region.objects.filter(id=form.cleaned_data.get("location_data")).first()

            if len(full_name) >= 3:
                first_name = full_name[0].capitalize()
                middle_name = full_name[1].capitalize()
                last_name = full_name[2].capitalize()
            elif len(full_name) == 2:
                first_name = full_name[0].capitalize()
                last_name = full_name[1].capitalize()
            else:
                raise ValidationError('Full name should either be three(3) or Two(2) names')

            email = form.cleaned_data.get("email").lower()    
            user_obj = User()
            user_obj.first_name = first_name
            user_obj.last_name = last_name
            user_obj.email = email
            user_obj.username = email
            user_obj.set_password(form.cleaned_data.get("password"))
            user_obj.save()
            user_obj.refresh_from_db()

            new_form = form.save(commit=False)
            new_form.user = user_obj
            new_form.middle_name = middle_name
            new_form.location = location
            new_form.user_type = form.cleaned_data.get("user_choice")
            new_form.save()

            tags = request.POST.getlist("tag")
            if len(tags) >= 1:
                for tag in tags:
                    tag_obj = Tag.objects.filter(id=tag).first()
                    if not UserTag.objects.filter(tag=tag_obj,is_active=True,is_deleted=False,user=user_obj).exists():
                        user_tag = UserTag()
                        user_tag.user = user_obj
                        user_tag.tag = tag_obj
                        user_tag.save()

            if user_obj:
                login(request, user_obj)
                if request.GET.get("next"):
                    return redirect(request.GET.get("next"))
                else:
                    return redirect('/')
        else:
            return render(request,"home/user_registration.html",{'form': form,'title': title})


class RegionsView(View):
    @method_decorator(never_cache)
    @method_decorator(login_required)
    @method_decorator(permission_required("control.view_region",login_url="/permission_denied/"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self,request,*args, **kwargs):
        regions = Region.objects.all().order_by("name")
        title = "Regions"
        context = {
            'title': title,
            'regions': regions
        }
        return render(request, "home/regions.html", context)
        
class AddRegionView(View):
    @method_decorator(never_cache)
    @method_decorator(login_required)
    @method_decorator(permission_required("control.add_region",login_url="/permission_denied/"))
    def dispatch(self, request, *args, **kwargs):
        return super(AddRegionView, self).dispatch(request, *args, **kwargs)

    def get(self, request,*args, **kwargs):
        context = {
            'form': RegionForm()
        }
        return render(request, "common/add_region.html", context)

    def post(self, request,*args, **kwargs):
        context = list()
        form = RegionForm(False, request.POST)
        if form.is_valid():
            form.save()
            info = {
                'status': True,
                'message': "Region successfully registered.."
            }
            context.append(info)
            return HttpResponse(json.dumps(context))
        else:
            return render(request, "common/add_region.html",{'form': form})


class EditRegionView(View):
    @method_decorator(never_cache)
    @method_decorator(login_required)
    @method_decorator(permission_required("control.change_region",login_url="/permission_denied/"))
    def dispatch(self, request, *args, **kwargs):
        return super(EditRegionView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        region = Region.objects.filter(id=kwargs.get("pk")).first()
        form = RegionForm(instance=region)
        context = {
            'form': form,
            'region': region,
        }
        return render(request, "common/edit_region.html", context)

    def post(self, request, *args, **kwargs):
        context = list()
        region = Region.objects.filter(id=kwargs.get("pk")).first()
        form = RegionForm(True, request.POST, instance=region)
        if form.is_valid():
            form.save()
            info = {
                'status': True,
                'message': "Region edited.."
            }
            context.append(info)
            return HttpResponse(json.dumps(context))
        else:
            return render(request, request, "common/edit_region.html",{'region': region,'form': form})



class DeleteRegionView(View):
    @method_decorator(never_cache)
    @method_decorator(login_required)
    @method_decorator(permission_required("control.delete_region",login_url='/permission_denied/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self,request,*args, **kwargs):
        context = list()
        region_id = kwargs.get("region_id")
        if Region.objects.filter(id=region_id):
            Region.objects.filter(id=region_id).delete()
            if not Region.objects.filter(id=region_id).exists():
                info = {
                    'status': True,
                    'message': "Region succesfully deleted"
                }
            else:
                info = {
                    'status': False,
                    'message': "Failed to delete region"
                }
        else:
            info = {
                'status': False,
                'message': "Region does not exists"
            }
        context.append(info)
        return HttpResponse(json.dumps(context))


class TagView(View):
    @method_decorator(never_cache)
    @method_decorator(login_required)
    @method_decorator(permission_required("control.view_tag",login_url="/permission_denied/"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self,request,*args, **kwargs):
        tags = Tag.objects.all()
        title = "Tags"
        context = {
            'title': title,
            'tags': tags
        }
        return render(request,"home/tags.html",context)


class AddTagView(View):
    @method_decorator(never_cache)
    @method_decorator(login_required)
    @method_decorator(permission_required("control.add_tag",login_url="/permission_denied/"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self,request,*args, **kwargs):
        form = TagForm(False)
        context = {
            'form': form,
        }
        return render(request,"common/add_tag.html",context)
    
    def post(self,request,*args, **kwargs):
        form = TagForm(False,request.POST)
        if form.is_valid():
            context = list()
            form.save()

            info = {
                'status': True,
                'message': "Tag saved successfully"
            }
            context.append(info)
            return HttpResponse(json.dumps(context))
        else:
            return render(request,"common/add_tag.html",{'form': form})
            
class EditTagView(View):
    @method_decorator(never_cache)
    @method_decorator(login_required)
    @method_decorator(permission_required("control.change_tag",login_url="/permission_denied/"))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self,request,*args, **kwargs):
        tag = Tag.objects.filter(id=kwargs.get("pk")).first()
        form = TagForm(True,instance=tag)
        context = {
            'form': form,
            'tag': tag
        }
        return render(request,"common/edit_tag.html",context)
    
    def post(self,request,*args, **kwargs):
        tag = Tag.objects.filter(id=kwargs.get("pk")).first()
        form = TagForm(True,request.POST,instance=tag)
        if form.is_valid():
            context = list()
            form.save()

            info = {
                'status': True,
                'message': "Tag saved successfully"
            }
            context.append(info)
            return HttpResponse(json.dumps(context))
        else:
            return render(request,"common/edit_tag.html",{'form': form,'tag': tag})


class AddPostView(View):
    @method_decorator(never_cache)
    @method_decorator(login_required)
    
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self,request,*args,**kwargs):
        user_obj = User.objects.filter(id=kwargs.get("pk")).first()
        form = StudentPostForm()
        title = "Student Post Registration"
        context = {
            'title': title,
            'form': form,
            'owner': user_obj
        }
        return render(request,"home/post_registration.html",context)
    
    def post(self,request,*args,**kwargs):
        user_obj = User.objects.filter(id=kwargs.get("pk")).first()
        form = StudentPostForm(request.POST)
        if form.is_valid():
            context = list()
            tags = ','.join([x[0] for x in Tag.objects.filter(id__in=request.POST.getlist("tag_name")).values_list("name")])
            print(tags)
            new_form = form.save(commit=False)
            new_form.owner = user_obj
            new_form.tags = tags
            new_form.save()

            from control.email_sender import send_email
            user_related = new_form.get_post_user_related()
            for u_obj in user_related:
                if new_form.tags in u_obj.profile.get_user_registered_tag():
                    email_body = f"Hello {u_obj.profile.get_full_name()}, There is new Post in Dev chat related to you"
                    user_email = u_obj.email
                    # user_email = "machabaezekiel@gmail.com"
                    send_email(subject='NEW POST NOTIFICATION',message=email_body,recipient=[user_email])
            
            info = {
                'status': True,
                'message': "Post saved successfully..",
                'url': reverse("home_page")
            }
            context.append(info)
            return HttpResponse(json.dumps(context))
        else:
            return render(request,"home/post_registration.html",{'form': form,'owner': user_obj})

    
class AddPostCommentView(View):
    @method_decorator(never_cache)
    @method_decorator(login_required)
    
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self,request,*args,**kwargs):
        user_obj = User.objects.filter(id=kwargs.get("pk")).first()
        post_obj = StudentPost.objects.filter(id=kwargs.get("post_id")).first()
        comments = PostComment.objects.filter(student_post=post_obj,is_active=True,is_deleted=False)
        form = PostCommentForm()
        context = {
            'form': form,
            'owner': user_obj,
            'post_obj': post_obj,
            'comments': comments
        }
        return render(request,"home/comment_registration.html",context)
    
    def post(self,request,*args,**kwargs):
        user_obj = User.objects.filter(id=kwargs.get("pk")).first()
        post_obj = StudentPost.objects.filter(id=kwargs.get("post_id")).first()
        post_obj = StudentPost.objects.filter(id=kwargs.get("post_id")).first()
        comments = PostComment.objects.filter(student_post=post_obj,is_active=True,is_deleted=False)

        form = PostCommentForm(request.POST)
        if form.is_valid():
            context = list()
            new_form = form.save(commit=False)
            new_form.owner = user_obj
            new_form.student_post = post_obj
            new_form.save()
            
            return redirect(reverse("add_post_comment",kwargs={'pk': user_obj.pk,'post_id': post_obj.pk}))
        else:
            return render(request,"home/comment_registration.html",{'form': form,'owner': user_obj,'post_obj': post_obj,'comments': comments})