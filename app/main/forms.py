#coding:utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,SubmitField,RadioField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User



class SearchForm(FlaskForm):
    gotime = StringField('出发日期（格式示例：2017/08/04）', default='2017/08/01',validators=[Length(10, 10)])
    backtime = StringField('返回日期（格式示例：2017/08/07）', default='2017/08/30', validators=[Length(10, 10)])
    limitmoney = StringField('预算费用', default=1000)
    scenic = StringField('最想去的景点', validators=[Length(0, 64)])
    submit1 = SubmitField('查询')

class EditProfileForm(FlaskForm):
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('联系地址', validators=[Length(0, 64)])
    about_me = TextAreaField('自我介绍')
    submit = SubmitField('提交！')

class ChangeScenicForm(FlaskForm):
    item = StringField('景点名称', validators=[DataRequired(), Length(1, 64)])
    intro = TextAreaField('介绍')
    opentime = StringField('开放时间', validators=[DataRequired(), Length(1, 64)])
    position = StringField('位置', validators=[DataRequired(), Length(1, 64)])
    price = StringField('门票价格', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('创建/更新景点信息')

class ChangeRouteForm(FlaskForm):
    item = StringField('线路名称', validators=[DataRequired(), Length(1, 64)])
    intro = TextAreaField('介绍')
    gotime = StringField('出发时间', validators=[DataRequired(), Length(1, 64)])
    backtime = StringField('返回时间', validators=[DataRequired(), Length(1, 64)])
    scenic = StringField('主要景点', validators=[DataRequired(), Length(1, 1024)])
    upper_num = StringField('每团人数上限', validators=[DataRequired(), Length(1, 64)])
    lower_num = StringField('最低开团人数', validators=[DataRequired(), Length(1, 64)])
    current_num = StringField('目前预约人数', validators=[DataRequired(), Length(1, 64)])
    price = StringField('价格', validators=[DataRequired(), Length(1, 64)])
    phone = StringField('联系电话', validators=[DataRequired(), Length(1, 64)])
    eat = StringField('饮食信息', validators=[DataRequired(), Length(1, 64)])
    sleep = StringField('住宿信息', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('创建/更新路线信息')

class SearchScenicForm(FlaskForm):
    item = StringField('景点名称', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('查找')

class EditProfileAdminForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64)])
    confirmed = BooleanField('验证状态')
    role = SelectField('用户组', coerce=int)
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('联系地址', validators=[Length(0, 64)])
    about_me = TextAreaField('自我介绍')
    submit = SubmitField('提交！')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已注册！')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在！')
