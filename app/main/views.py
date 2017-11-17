#coding:utf-8
from __future__ import division
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from flask import render_template, redirect, url_for,  flash
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, ChangeScenicForm,ChangeRouteForm,SearchForm
from .. import db
from ..models import Role, User, Scenic, Route
from ..decorators import admin_required
from operator import attrgetter
from flask import send_file, send_from_directory
import os
from tripweb import app

@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@main.route('/scenic', methods=['GET', 'POST'])
@login_required
def scenic():
    scenics = Scenic.query.order_by(Scenic.item.desc()).all()
    return render_template('scenic.html', scenics=scenics)

@main.route('/scenic_price_uptodown', methods=['GET', 'POST'])
def scenic_price_uptodown():
    scenics = Scenic.query.order_by(Scenic.item.desc()).all()
    return render_template('scenic.html', scenics=sorted(scenics, key=attrgetter('price'), reverse=True))

@main.route('/scenic_price_downtoup', methods=['GET', 'POST'])
def scenic_price_downtoup():
    scenics = Scenic.query.order_by(Scenic.item.desc()).all()
    return render_template('scenic.html', scenics=sorted(scenics, key=attrgetter('price')))

@main.route('/scenic_evaluate_uptodown', methods=['GET', 'POST'])
def scenic_evaluate_uptodown():
    scenics = Scenic.query.order_by(Scenic.item.desc()).all()
    return render_template('scenic.html', scenics=sorted(scenics, key=attrgetter('evaluate'), reverse=True))

@main.route('/scenic_evaluate_downtoup', methods=['GET', 'POST'])
def scenic_evaluate_downtoup():
    scenics = Scenic.query.order_by(Scenic.item.desc()).all()
    return render_template('scenic.html', scenics=sorted(scenics, key=attrgetter('evaluate')))

@main.route('/scenic_popular_uptodown', methods=['GET', 'POST'])
def scenic_popular_uptodown():
    scenics = Scenic.query.order_by(Scenic.item.desc()).all()
    return render_template('scenic.html', scenics=sorted(scenics, key=attrgetter('visit_num'), reverse=True))

@main.route('/scenic_popular_downtoup', methods=['GET', 'POST'])
def scenic_popular_downtoup():
    scenics = Scenic.query.order_by(Scenic.item.desc()).all()
    return render_template('scenic.html', scenics=sorted(scenics, key=attrgetter('visit_num')))

@main.route('/order_route/<order_num>,<item>,<user>,<phone>', methods=['GET', 'POST'])
@login_required
def order_route(order_num,item,user,phone):
    route1 = Route.query.filter_by(item=item).first_or_404()
    sce = str(route1.scenic).split(' ')
    for s in sce:
        s1=Scenic.query.filter_by(item=s).first()
        if s1 is not None:
            s1.order_data = s1.order_data + str('联系人姓名：'+user
                                                +' 预约人数：'+order_num
                                                +' 联系电话：'+phone
                                                +' 游览开始最早日期：'+route1.gotime
                                                +' 游览结束最晚日期：'+route1.backtime+'\n')
    route1.current_num = route1.current_num + int(order_num)
    route1.order_data = route1.order_data + str('联系人姓名：'+user+' 预约人数：'+order_num+' 联系电话：'+phone+'\n')
    user_route_all = str(current_user.route)
    user_route_now = str(route1.item)
    if user_route_all.find(user_route_now) == -1:
        current_user.route = current_user.route + str('#'+route1.item)
        current_user.score = current_user.score + 1
        flash('预约成功，可到个人资料中查看预约记录.')
    else:
        flash('您已预约过此路线，可到个人资料中查看.')
    return redirect(url_for('.route', item=item))

@main.route('/focus_scenic/<item>', methods=['GET', 'POST'])
@login_required
def focus_scenic(item):
    sce1 = Scenic.query.filter_by(item=item).first_or_404()
    scenic_user_all = str(current_user.scenic)
    scenic_user_current = str(sce1.item)
    if scenic_user_all.find(scenic_user_current) == -1:
        current_user.scenic = current_user.scenic + str('#'+sce1.item)
        flash('收藏成功，可到个人资料中查看.')
    else:
        flash('您已收藏过此景点，可到个人资料中查看.')
    return render_template('scenic.html',sce1=sce1)

@main.route('/change_scenic', methods=['GET', 'POST'])
@login_required
def change_scenic():
    form = ChangeScenicForm()
    if form.validate_on_submit():
        sce1 = Scenic.query.filter_by(item=form.item.data).first()
        sce = Scenic(item=form.item.data,
                     intro=form.intro.data,
                     opentime=form.opentime.data,
                     position=form.position.data,
                     price=form.price.data)
        if sce1 is not None:
            flash('数据库中已经有该景点，我们为您进行了数据更新.')
            db.session.delete(sce1)
            db.session.add(sce)
        else:
            db.session.add(sce)
            flash('这是一个新的景点，我们将其加入了数据库中，供游客查询.')
        return render_template('scenic.html')
    return render_template('change_scenic.html', form=form)

@main.route('/change_route/<user>', methods=['GET', 'POST'])
@login_required
def change_route(user):
    form = ChangeRouteForm()
    user1 = User.query.filter_by(username=user).first()
    if form.validate_on_submit():
        route1 = Route.query.filter_by(item=form.item.data).first()
        route = Route(item=form.item.data,
                     intro=form.intro.data,
                     gotime=form.gotime.data,
                     backtime=form.backtime.data,
                     scenic=form.scenic.data,
                     upper_num=form.upper_num.data,
                     lower_num=form.lower_num.data,
                     current_num=form.current_num.data,
                     phone=form.phone.data,
                     eat=form.eat.data,
                     sleep=form.sleep.data,
                     price=form.price.data,
                     company=user1.company)
        if route1 is not None:
            flash('数据库中已经有该路线，我们为您进行了数据更新.')
            db.session.delete(route1)
            db.session.add(route)
        else:
            db.session.add(route)
            flash('这是一条新的路线，我们将其加入了数据库中，供游客查询.')
        return render_template('route.html')
    return render_template('change_route.html', form=form)


@main.route('/del_scenic/<item>', methods=['GET', 'POST'])
@login_required
def del_scenic(item):
    sce1 = Scenic.query.filter_by(item=item).first_or_404()
    if current_user.is_SCENICER():
        flash('指定的景点已被移除.')
        db.session.delete(sce1)
        return redirect(url_for('.scenic'))
    return render_template('scenic.html',sce1=sce1)

@main.route('/del_route/<item>', methods=['GET', 'POST'])
@login_required
def del_route(item):
    route1 = Route.query.filter_by(item=item).first_or_404()
    if current_user.is_ROUTER():
        flash('指定的路线已被移除.')
        db.session.delete(route1)
        return redirect(url_for('.route'))
    return render_template('route.html',route1=route1)

@main.route('/eva_scenic/<eva>,<item>', methods=['GET', 'POST'])
@login_required
def eva_scenic(eva,item):
    item1 = Scenic.query.filter_by(item=item).first_or_404()
    eva_all = item1.evaluate * item1.visit_num + int(eva)
    item1.visit_num = item1.visit_num + 1
    item1.evaluate = eva_all / item1.visit_num
    return redirect(url_for('.scenic', item=item1))

@main.route('/complain_scenic/<item>', methods=['GET', 'POST'])
@login_required
def complain_scenic(item):
    item1 = Scenic.query.filter_by(item=item).first_or_404()
    item1.complain = item1.complain + 1
    flash('您的投诉已被受理，稍后有景区工作人员联系您')
    return redirect(url_for('.scenic', item=item1))

@main.route('/route', methods=['GET', 'POST'])
@login_required
def route():
    routes = Route.query.order_by(Route.item.desc()).all()
    return render_template('route.html', routes=routes)

@main.route('/route_user/<r>', methods=['GET', 'POST'])
def route_user(r):
    route1 = Route.query.filter_by(item=r).all()
    return render_template('route.html', routes=route1)

@main.route('/scenic_user/<s>', methods=['GET', 'POST'])
def scenic_user(s):
    scenic = Scenic.query.filter_by(item=s).all()
    return render_template('scenic.html', scenics=scenic)


@main.route('/indiv', methods=['GET', 'POST'])
@login_required
def indiv():
    form = SearchForm()
    if form.validate_on_submit():
        gotime = str(form.gotime.data)
        backtime = str(form.backtime.data)
        limitmoney = form.limitmoney.data
        scenic = str(form.scenic.data)
        route1 = Route.query.filter(Route.price <= limitmoney,
                                    Route.gotime >= gotime,
                                    Route.backtime <= backtime,
                                    Route.scenic.ilike('%' + scenic + '%')).all()
        return render_template('route.html', routes=route1)
    return render_template('indiv.html', form=form)

@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    routes = Route.query.filter_by(company=user.company).all()
    scenics = Scenic.query.filter_by().all()
    route = str(user.route).split('#')
    scenic = str(user.scenic).split('#')
    l_sce = len(scenic)
    l_rou = len(route)
    route1 = route[1:l_rou]
    scenic1 = scenic[1:l_sce]
    return render_template('user.html',route1=route1,scenic1=scenic1,routes=routes,scenics=scenics,user=user)

@main.route('/route_printf/<item>')
@login_required
def route_print(item):
    route = Route.query.filter_by(item=item).first()
    f = open("./app/static/%s.txt"%item, "w")
    f.write('线路名称：%s\n线路介绍：%s\n出发时间：%s\n返回时间：%s\n主要景点：%s\n最大人数：%s\n最小人数：%s\n联系电话：%s\n饮食信息：%s\n住宿信息：%s\n价格：%s\n旅行社名称：%s'%(route.item,route.intro,route.gotime,route.backtime,route.scenic,route.upper_num,route.lower_num,route.phone,route.eat,route.sleep,route.price,route.company))
    f.close()
    dirpath = os.path.join(app.root_path, 'static')
    return send_from_directory(dirpath,filename='%s.txt'%item, as_attachment=True)

@main.route('/scenic_printf')
@login_required
def scenic_printf():
    sces = Scenic.query.filter_by().all()
    f = open("./app/static/scenic_order.txt", "w")
    for s in sces:
        f.write('景点名称：%s 预约情况：\n%s\n'%(s.item,s.order_data))
    f.close()
    dirpath = os.path.join(app.root_path, 'static')
    return send_from_directory(dirpath,filename='scenic_order.txt', as_attachment=True)

@main.route('/company_route_print/<company>')
@login_required
def company_route_print(company):
    routes = Route.query.filter_by(company=company).all()
    f = open("./app/static/route_order.txt", "w")
    for r in routes:
        f.write('线路名称：%s 共有%s人预约，预约情况：\n%s\n' % (r.item,r.current_num,r.order_data))
    f.close()
    dirpath = os.path.join(app.root_path, 'static')
    return send_from_directory(dirpath, filename='route_order.txt', as_attachment=True)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('个人资料修改成功！')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/user_admin', methods=['GET', 'POST'])
@login_required
@admin_required
def user_admin():
    users = User.query.filter_by().all()
    return render_template('user_admin.html', users=users)

@main.route('/del_user/<email>', methods=['GET', 'POST'])
@login_required
@admin_required
def del_user(email):
    user = User.query.filter_by(email=email).first()
    flash('用户数据删除成功！')
    db.session.delete(user)
    return render_template('user_admin.html')
