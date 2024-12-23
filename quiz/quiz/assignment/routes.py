import os

from quiz import app, db
from flask_login import  current_user,  login_required
from quiz.forms import AddAssignment 
from quiz.models import User, Class,Assignment ,Assignment_Score
from werkzeug.utils import secure_filename
from flask import render_template, redirect, session, url_for,  flash, current_app, send_from_directory, send_file, request
from quiz.utils import assignment_added_email 
from datetime import datetime
from quiz.quiz.routes import get_file_extension


@app.route('/add_assignment', methods=['GET', 'POST'])
@login_required
def add_assignment():
    current_classid = session.get('current_classid')
    user_classes = Class.query.filter_by(creator_id=current_user.id).all()
    form = AddAssignment()
    
    if form.validate_on_submit():
        title = form.assignmenttitle.data
        description = form.assignmentdescription.data
        due_date = form.duedate.data
        due_time = request.form.get('due_time')
        due_datetime_str = f"{due_date} {due_time}"

        due_date = datetime.strptime(due_datetime_str, '%Y-%m-%d %H:%M')
        points = form.points.data
        class_id = current_classid
        attachment = form.attachment.data  
        extension = get_file_extension(attachment)
        if attachment:  
            if extension == '.pdf' or '.docx' or '.txt' :
        
                filename = secure_filename(attachment.filename)
                attachment_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                attachment.save(attachment_path)  # Save the file

                assignment = Assignment(title=title, description=description, due_date=due_date,points=points,
                                        class_id=class_id, creator_id=current_user.id,
                                        file_attachment=attachment_path)
                db.session.add(assignment)
                db.session.commit()
                send_email(assignment)
                flash('Assignment created successfully!', 'success')
            else:
                flash('File type not allowed','danger')
        return redirect(url_for('class_info', classid=current_classid))

    return render_template('addassignment.html', form=form, user_classes=user_classes)

def send_email(assignment): 
        classid = assignment.class_id
        classs = Class.query.get(classid)
        users = User.query.all()
        title = assignment.title
        msgbody = f'Assignment Added in {classs.class_name} Due-Date:{assignment.due_date}-----------{assignment.description}'
        for user in users: 
            if classs in user.classes: 
                assignment_added_email(user,title=title, msgbody=msgbody)

@app.route('/download_attachment/<filename>', methods=['GET'])
def download_attachment(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        # Handle the case where the file does not exist
        return "File not found", 404

@app.route('/assignment/<int:assignment_id>')
def assignment_details(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    submitted_assignments = Assignment_Score.query.filter_by(assignment_id=assignment_id).all()
    turned_in = len(submitted_assignments)
    participants = session.get('participants')

    if assignment.file_attachment:
        filename = os.path.basename(assignment.file_attachment)
    
    return render_template('assignmentdetails.html', assignment=assignment, current_user=current_user, 
    filename=filename, submitted_assignment=submitted_assignments, turned_in=turned_in, participants=participants)

@app.route('/uploadassignment-<int:assignment_id>', methods=['GET', 'POST'])
def upload_assignment(assignment_id):
    if request.method == 'POST':
        uploaded_file = request.files['fileInput']
        
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            attachment_path = os.path.join(current_app.config['SUBMIT_FOLDER'], filename)
            uploaded_file.save(attachment_path)
            a_assignment = Assignment.query.get_or_404(assignment_id)
            assignment = Assignment_Score(assignment_id=assignment_id,student_username=current_user.username,class_id=session.get('current_classid'),
                                          uploaded_assignment=attachment_path ,points=a_assignment.points)
            db.session.add(assignment)
            db.session.commit()

    return redirect(url_for('assignment_details', assignment_id=assignment_id))

@app.route('/download_upload/<filename>', methods=['GET'])
def download_upload(filename):
    file_path = os.path.join(app.config['SUBMIT_FOLDER'], filename)
    
    return send_file(file_path, as_attachment=True)
 
@app.route('/assignment_score/<int:assignment_id>', methods=['GET', 'POST'])
def assignment_score(assignment_id):
    assignment = Assignment_Score.query.get_or_404(assignment_id)
    if assignment and request.method == 'POST':
        points = request.form.get('score')
        assignment.points_scored = points
        
        db.session.commit()
    return redirect(url_for('assignment_details', assignment_id=assignment_id))

@app.route('/<int:assignment_id>/delete')
def delete_assignment(assignment_id): 
    assignment = Assignment.query.get_or_404(assignment_id)
    classid = assignment.class_id
    db.session.delete(assignment)
    db.session.commit()
    return redirect(url_for('class_info',classid=classid))
