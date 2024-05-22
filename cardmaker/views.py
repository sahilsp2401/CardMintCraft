from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from cardmaker.models import Contact,Usercomment,VisitingCard,IdCard,Resume
from math import ceil
from reportlab.pdfgen import canvas
from PIL import Image
import os
import json
from reportlab.lib.utils import ImageReader

# Create your views here.

def home(request):
    return render(request,'cardmaker/home.html')

def contact(request):
    if request.method =='POST' :
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        content = request.POST['content']

        if len(name)<2 or len(email)<3 or len(phone)<10 or len(content)<4 :
            messages.error(request,'Please fill the form correctly')
        else:
            contact = Contact(name=name, email=email, phone=phone, content=content) 
            contact.save()
            messages.success(request,'Your message has been sent successfully')
    return render(request,'cardmaker/contact.html')

def about(request):
    return render(request,'cardmaker/about.html')

def comment(request):
    return render(request,'cardmaker/comment.html')

def handleSignup(request):
    if request.method == 'POST':
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if len(username) > 10:
            messages.error(request,"Username must be under 10 character.")
            return redirect('home')
        if not username.isalnum():
            messages.error(request,"Username should only contains letters and numbers ")
            return redirect('home')
        if pass1 != pass2 :
            messages.error(request,"Passwords do not match.")
            return redirect('home')


        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        messages.success(request,"Your iCoder account has been successfully created!")
        return redirect('home')
    else:
        return HttpResponse("404 - Not Found")

def handleLogin(request):
    if request.method == 'POST':
        loginusername= request.POST['loginusername']
        loginpass = request.POST['loginpass']

        user = authenticate(username=loginusername , password=loginpass )

        if user is not None:
            login(request,user)
            messages.success(request,"Successfully Logged In")
            return redirect('home')
        else:
            messages.error(request,"Invalid Credentials,Please try again")
            return redirect('home')

    return HttpResponse("404 - Not Found")

def handleLogout(request):
    logout(request)
    messages.success(request,"Successfully Logged Out")
    return redirect('home')

def viewComment(request):
    comments = Usercomment.objects.filter(parent=None)
    replies = Usercomment.objects.exclude(parent=None)
    repDict = {}
    for reply in replies:
        if reply.parent.sno not in repDict.keys():
            repDict[reply.parent.sno] = [reply]
        else:
            repDict[reply.parent.sno].append(reply)

    context = {'comments':comments,'user':request.user,'replyDict':repDict}
    return render(request,'cardmaker/comment.html',context)


def postComment(request):
    if request.method=="POST":
        comment = request.POST.get("comment")
        parentSno = request.POST.get('parentSno')
        user = request.user
        if parentSno == "":
            comment = Usercomment(comment=comment,user=user)
            comment.save()
            messages.success(request,"Your comment has been posted succssfully")
        else:
            parent = Usercomment.objects.get(sno=parentSno)
            comment = Usercomment(comment=comment,user=user,parent=parent)
            comment.save()
            messages.success(request,"Your reply has been posted succssfully")
    
    return redirect(f"/viewComment")

# Visiting card

def visitingcard(request):
    cards = VisitingCard.objects.all()
    cards = list(cards)
    n = len(cards)
    nSlides = n//4 + ceil((n/4)-(n//4))
    allCards = [[cards,range(1,nSlides),nSlides]]
    params = {'allCards':allCards}
    return render(request,"cardmaker/visitingcard.html",params)

def load_template(card_id):
    template_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'templates',
        'card_templates.json'
    )
    
    with open(template_file_path, 'r') as template_file:
        templates = json.load(template_file)

    template = templates.get(str(card_id))
    return template

def generate_visiting_card(request):
    if request.method == 'POST':
        card_id = int(request.POST.get('id'))
        logo = request.FILES.get('logo', None)
        tagline = request.POST.get('tagline')
        owner = request.POST.get('name')
        address = request.POST.get('address')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        card = VisitingCard.objects.filter(id=card_id).first()
        front_design = card.front_image
        back_design = card.back_image

        template = load_template(card_id)

        front_img = Image.open(front_design)
        back_img = Image.open(back_design)
        front_width, front_height = front_img.size
        back_width, back_height = back_img.size

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="visiting_card.pdf"'
        p = canvas.Canvas(response, pagesize=(front_width, front_height))
 
        p.drawImage(front_design.path, x=0, y=0, width=front_width, height=front_height)

        if logo:
            logo_img = Image.open(logo)
            logo_img = logo_img.convert("RGBA")
            max_logo_width = 800
            max_logo_height = 400
            logo_img.thumbnail((max_logo_width, max_logo_height))
            logo_width, logo_height = logo_img.size
            logo_coordinates = template.get("logo", {})
            logo_x = logo_coordinates.get("x", 0)
            logo_y = logo_coordinates.get("y", 0)
            logo_image_reader = ImageReader(logo_img)
            p.drawImage(logo_image_reader, x=logo_x, y=logo_y, width=logo_width, height=logo_height, mask='auto')

            tagline_coordinates = template.get("tagline", {})
            tagline_x = tagline_coordinates.get('x',0)
            tagline_y = tagline_coordinates.get('y',0)
            p.setFont("Helvetica", 25)
            p.drawString(tagline_x, tagline_y, f"{tagline}")
            p.showPage()

        p.setPageSize((back_width, back_height))
        p.drawImage(back_design.path, x=0, y=0, width=back_width, height=back_height)

        phone_coordinates = template.get("phone", {})
        email_coordinates = template.get("email", {})
        address_coordinates = template.get("address", {})
        phone_x = phone_coordinates.get("x", 0)
        phone_y = phone_coordinates.get("y", 0)
        email_x = email_coordinates.get("x", 0)
        email_y = email_coordinates.get("y", 0)
        address_x = address_coordinates.get("x", 0)
        address_y = address_coordinates.get("y", 0)
        owner_coordinates = template.get("owner", {})
        owner_x = owner_coordinates.get("x", 0)
        owner_y = owner_coordinates.get("y", 0)
        p.setFont("Helvetica", 25)
        p.drawString(owner_x, owner_y, f"{owner}")
        p.drawString(phone_x,phone_y, f"{phone}")
        p.drawString(email_x, email_y, f"{email}")
        p.drawString(address_x, address_y, f"{address}")


        p.showPage()
        p.save()

        return response

    else:
        return render(request,"cardmaker/home.html")
    

def idcard(request):
    cards = IdCard.objects.all()
    cards = list(cards)
    n = len(cards)
    nSlides = n//4 + ceil((n/4)-(n//4))
    allCards = [[cards,range(1,nSlides),nSlides]]
    params = {'allCards':allCards}
    return render(request,"cardmaker/idcard.html",params)

def load_idtemplate(card_id):
    template_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'templates',
        'card_idtemplates.json'
    )
    
    with open(template_file_path, 'r') as template_file:
        templates = json.load(template_file)

    template = templates.get(str(card_id))
    return template

def generate_id_card(request):
    if request.method == 'POST':
        card_id = int(request.POST.get('id'))
        logo = request.FILES.get('logo', None)
        photo = request.FILES.get('photo', None)
        name = request.POST.get('name')
        id = request.POST.get('idnumber')
        blood = request.POST.get('blood')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        card = IdCard.objects.filter(id=card_id).first()
        design = card.image

        template = load_idtemplate(card_id)

        img = Image.open(design)
        img_width, img_height = img.size

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="id_card.pdf"'
        p = canvas.Canvas(response, pagesize=(img_width, img_height))
 
        p.drawImage(design.path, x=0, y=0, width=img_width, height=img_height)

        if photo:
            photo_img = Image.open(photo)
            photo_img = photo_img.convert("RGBA")
            max_photo_width = 500
            max_photo_height = 250
            photo_img.thumbnail((max_photo_width, max_photo_height))
            photo_width, photo_height = photo_img.size
            photo_coordinates = template.get("photo", {})
            photo_x = photo_coordinates.get("x", 0)
            photo_y = photo_coordinates.get("y", 0)
 
            photo_image_reader = ImageReader(photo_img)
            p.drawImage(photo_image_reader, x=photo_x, y=photo_y, width=photo_width, height=photo_height, mask='auto')

            name_coordinates = template.get("name", {})
            name_x = (img_width - p.stringWidth(name, "Helvetica", 25)) / 2
            name_y = photo_y - 40 
            p.setFont("Helvetica", 25)
            p.drawString(name_x, name_y, f"{name}")

        if logo:
            logo_img = Image.open(logo)
            logo_img = logo_img.convert("RGBA")
            max_logo_width = 200
            max_logo_height = 100
            logo_img.thumbnail((max_logo_width, max_logo_height))
            logo_width, logo_height = logo_img.size
            logo_coordinates = template.get("logo", {})
            logo_x = logo_coordinates.get("x", 0)
            logo_y = logo_coordinates.get("y", 0)
            logo_image_reader = ImageReader(logo_img)
            p.drawImage(logo_image_reader, x=logo_x, y=logo_y, width=logo_width, height=logo_height, mask='auto')

        id_coordinates = template.get("id", {})
        phone_coordinates = template.get("phone", {})
        email_coordinates = template.get("email", {})
        blood_coordinates = template.get("blood", {})
        id_x = id_coordinates.get("x", 0)
        id_y = id_coordinates.get("y", 0)
        phone_x = phone_coordinates.get("x", 0)
        phone_y = phone_coordinates.get("y", 0)
        email_x = email_coordinates.get("x", 0)
        email_y = email_coordinates.get("y", 0)
        blood_x = blood_coordinates.get("x", 0)
        blood_y = blood_coordinates.get("y", 0)
        p.setFont("Helvetica", 25)
        p.drawString(id_x, id_y, f"{id}")
        p.drawString(blood_x, blood_y , f"{blood}")
        p.drawString(email_x, email_y, f"{email}")
        p.drawString(phone_x, phone_y, f"{phone}")


        p.showPage()
        p.save()

        return response

    else:
        return render(request,"cardmaker/home.html")


def resume(request):
    cards = Resume.objects.all()
    cards = list(cards)
    n = len(cards)
    nSlides = n//4 + ceil((n/4)-(n//4))
    allCards = [[cards,range(1,nSlides),nSlides]]
    params = {'allCards':allCards}
    return render(request,"cardmaker/resume.html",params)

def load_resumetemplate(card_id):
    template_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'templates',
        'card_resumetemplates.json'
    )
    
    with open(template_file_path, 'r') as template_file:
        templates = json.load(template_file)

    template = templates.get(str(card_id))
    return template

def generate_resume_card(request):
    if request.method == 'POST':
        card_id = int(request.POST.get('id'))
        profile = request.POST.get('profile')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        link = request.POST.get('link')
        summary1 = request.POST.get('summary1')
        summary2 = request.POST.get('summary2')
        e_sname = request.POST.get('sname')
        e_sper = request.POST.get('sper')
        e_syear = request.POST.get('syear')
        e_cname = request.POST.get('cname')
        e_cper = request.POST.get('cper')
        e_cyear = request.POST.get('cyear')
        e_gname = request.POST.get('gname')
        e_gper = request.POST.get('gper')
        e_gyear = request.POST.get('gyear')
        s_tskills = request.POST.get('tskills')
        s_sskills = request.POST.get('sskills')
        l_flang = request.POST.get('flang')
        l_slang = request.POST.get('slang')
        l_tlang = request.POST.get('tlang')
        card = Resume.objects.filter(id=card_id).first()
        design = card.image

        template = load_resumetemplate(card_id)

        img = Image.open(design)
        img_width, img_height = img.size

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="resume.pdf"'
        p = canvas.Canvas(response, pagesize=(img_width, img_height))
 
        p.drawImage(design.path, x=0, y=0, width=img_width, height=img_height)

        name_coordinates = template.get("name", {})
        profile_coordinates = template.get("profile", {})
        phone_coordinates = template.get("phone", {})
        email_coordinates = template.get("email", {})
        address_coordinates = template.get("address",{})
        link_coordinates = template.get("link",{})
        summary1_coordinates = template.get("summary1",{})
        summary2_coordinates = template.get("summary2",{})
        e_sname_coordinates = template.get("e_sname",{})
        e_sper_coordinates = template.get("e_sper",{})
        e_syear_coordinates = template.get("e_syear",{})
        e_cname_coordinates = template.get("e_cname",{})
        e_cper_coordinates = template.get("e_cper",{})
        e_cyear_coordinates = template.get("e_cyear",{})
        e_gname_coordinates = template.get("e_gname",{})
        e_gper_coordinates = template.get("e_gper",{})
        e_gyear_coordinates = template.get("e_gyear",{})
        s_tskills_coordinates = template.get("s_tskills",{})
        s_sskills_coordinates = template.get("s_sskills",{})
        l_flang_coordinates = template.get("l_flang",{})
        l_slang_coordinates = template.get("l_slang",{})
        l_tlang_coordinates = template.get("l_tlang",{})

        name_x = name_coordinates.get("x",0)
        name_y = name_coordinates.get("y",0)
        profile_x = profile_coordinates.get("x",0)
        profile_y = profile_coordinates.get("y",0)
        phone_x = phone_coordinates.get("x", 0)
        phone_y = phone_coordinates.get("y", 0)
        email_x = email_coordinates.get("x", 0)
        email_y = email_coordinates.get("y", 0)
        address_x = address_coordinates.get("x", 0)
        address_y = address_coordinates.get("y", 0)
        link_x = link_coordinates.get("x", 0)
        link_y = link_coordinates.get("y", 0)
        summary1_x = summary1_coordinates.get("x", 0)
        summary1_y = summary1_coordinates.get("y", 0)
        summary2_x = summary2_coordinates.get("x", 0)
        summary2_y = summary2_coordinates.get("y", 0)
        e_sname_x = e_sname_coordinates.get("x", 0)
        e_sname_y = e_sname_coordinates.get("y", 0)
        e_sper_x =  e_sper_coordinates.get("x", 0)
        e_sper_y =  e_sper_coordinates.get("y", 0)
        e_syear_x =  e_syear_coordinates.get("x", 0)
        e_syear_y =  e_syear_coordinates.get("y", 0)
        e_cname_x = e_cname_coordinates.get("x", 0)
        e_cname_y = e_cname_coordinates.get("y", 0)
        e_cper_x =  e_cper_coordinates.get("x", 0)
        e_cper_y =  e_cper_coordinates.get("y", 0)
        e_cyear_x =  e_cyear_coordinates.get("x", 0)
        e_cyear_y =  e_cyear_coordinates.get("y", 0)
        e_gname_x = e_gname_coordinates.get("x", 0)
        e_gname_y = e_gname_coordinates.get("y", 0)
        e_gper_x =  e_gper_coordinates.get("x", 0)
        e_gper_y =  e_gper_coordinates.get("y", 0)
        e_gyear_x =  e_gyear_coordinates.get("x", 0)
        e_gyear_y =  e_gyear_coordinates.get("y", 0)
        s_tskills_x = s_tskills_coordinates.get("x", 0)
        s_tskills_y = s_tskills_coordinates.get("y", 0)
        s_sskills_x = s_sskills_coordinates.get("x", 0)
        s_sskills_y = s_sskills_coordinates.get("y", 0)
        l_flang_x = l_flang_coordinates.get("x", 0)
        l_flang_y = l_flang_coordinates.get("y", 0)
        l_slang_x = l_slang_coordinates.get("x", 0)
        l_slang_y = l_slang_coordinates.get("y", 0)
        l_tlang_x = l_tlang_coordinates.get("x", 0)
        l_tlang_y = l_tlang_coordinates.get("y", 0)

        p.setFont("Helvetica", 100)

        p.drawString(name_x, name_y, f"{name}")
        p.drawString(profile_x, profile_y, f"{profile}")
        p.setFont("Helvetica", 69)
        p.drawString(email_x, email_y, f"{email}")
        p.drawString(phone_x, phone_y, f"{phone}")
        p.drawString(address_x, address_y, f"{address}")
        p.drawString(link_x, link_y, f"{link}")
        p.drawString(e_sname_x, e_sname_y, f"{e_sname}")
        p.drawString(e_sper_x, e_sper_y, f"{e_sper}")
        p.drawString(e_syear_x, e_syear_y, f"{e_syear}")
        p.drawString(e_cname_x, e_cname_y, f"{e_cname}")
        p.drawString(e_cper_x, e_cper_y, f"{e_cper}")
        p.drawString(e_cyear_x, e_cyear_y, f"{e_cyear}")
        p.drawString(e_gname_x, e_gname_y, f"{e_gname}")
        p.drawString(e_gper_x, e_gper_y, f"{e_gper}")
        p.drawString(e_gyear_x, e_gyear_y, f"{e_gyear}")
        p.drawString(l_flang_x, l_flang_y, f"{l_flang}")
        p.drawString(l_slang_x, l_slang_y, f"{l_slang}")
        p.drawString(l_tlang_x, l_tlang_y, f"{l_tlang}")


        p.setFont("Helvetica",39)
        p.drawString(summary1_x, summary1_y, f"{summary1}")
        p.drawString(summary2_x, summary2_y, f"{summary2}")

        p.setFont("Helvetica",27)
        p.drawString(s_tskills_x, s_tskills_y, f"{s_tskills}")
        p.drawString(s_sskills_x, s_sskills_y, f"{s_sskills}")
        p.showPage()
        p.save()

        return response

    else:
        return render(request,"cardmaker/home.html")



