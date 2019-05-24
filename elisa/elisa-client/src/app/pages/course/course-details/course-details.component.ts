import {Component, Inject, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material';
import {Course} from '../../../models/course';
import {CourseService} from '../../../services/course.service';

@Component({
  selector: 'app-course-details',
  templateUrl: './course-details.component.html',
  styleUrls: ['./course-details.component.less']
})
export class CourseDetailsComponent implements OnInit {

  courseForm: FormGroup;
  newCourse: boolean = false;

  constructor(
    public dialogRef: MatDialogRef<CourseDetailsComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private courseService: CourseService,
  ) { }

  ngOnInit() {
    if(!this.data.course){
      this.newCourse = true;
      this.data.course = new Course();
    }
    this.courseForm = new FormGroup({
      'code': new FormControl(this.data.course.code,[
        Validators.required,
      ]),
      'name': new FormControl(this.data.course.name,[
        Validators.required,
      ]),
      'department': new FormControl(this.data.course.department,[
        Validators.required,
      ]),
      'completion': new FormControl(this.data.course.completion,[
        Validators.required,
      ]),
    });
  }

  removeCourse() {
    this.courseService.deleteCourse(this.data);
    this.dialogRef.close(true);
  }

  onSubmit(){
    let post = this.courseForm.value;
    if(this.newCourse){
      this.courseService.createCourse(post);
    }
    else{
      this.courseService.updateCourse(post);
    }
    this.dialogRef.close(true);
  }
}
