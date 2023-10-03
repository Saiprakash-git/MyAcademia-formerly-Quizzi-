import os 
from quiz import app, db
from flask_login import  current_user,  login_required
from quiz.forms import AddAssignment 
from quiz.models import User, Class,Assignment 
from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for,  flash, current_app, send_from_directory, send_file
from quiz.utils import assignment_added_email


@app.route('/add_assignment', methods=['GET', 'POST'])
@login_required
def add_assignment():
    user_classes = Class.query.filter_by(creator_id=current_user.id).all()
    form = AddAssignment()
    form.class_id.choices = [(class_.id, class_.class_name) for class_ in user_classes]

    if form.validate_on_submit():
        title = form.assignmenttitle.data
        description = form.assignmentdescription.data
        due_date = form.duedate.data
        class_id = form.class_id.data
        attachment = form.attachment.data  # Get the uploaded file

        if attachment:  # Check if a file was uploaded
            filename = secure_filename(attachment.filename)
            attachment_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            attachment.save(attachment_path)  # Save the file

        assignment = Assignment(title=title, description=description, due_date=due_date,
                                class_id=class_id, creator_id=current_user.id,
                                file_attachment=attachment_path)
        db.session.add(assignment)
        db.session.commit()
        # send_email(assignment)
        flash('Assignment created successfully!', 'success')
        return redirect(url_for('class_info', classid=form.class_id.data))

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
    if assignment.file_attachment:
        filename = os.path.basename(assignment.file_attachment)
    return render_template('assignmentdetails.html', assignment=assignment, current_user=current_user, filename=filename)

@app.route('/<int:assignment_id>/delete')
def delete_assignment(assignment_id): 
    assignment = Assignment.query.get_or_404(assignment_id)
    classid = assignment.class_id
    db.session.delete(assignment)
    db.session.commit()
    return redirect(url_for('class_info',classid=classid))
