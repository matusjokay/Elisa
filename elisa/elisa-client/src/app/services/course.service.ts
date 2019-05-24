import { Injectable } from '@angular/core';
import {Observable} from 'rxjs';
import {environment} from '../../environments/environment';
import {map} from 'rxjs/operators';
import {HttpClient} from '@angular/common/http';
import {Course} from '../models/course';

@Injectable({
  providedIn: 'root'
})
export class CourseService {

  constructor(private http: HttpClient) { }

  getAll(): Observable<Course[]>{
    return this.http.get<Course[]>(environment.APIUrl + "courses/").pipe(
      map((response: any) => {
        return response;
        }
      ));
  }

  getCoursesByTeacherMap(): Observable<Course[]>{
    return this.http.get<Course[]>(environment.APIUrl + "teachers/").pipe(
      map((response: any) => {
        return response.reduce(function(r, e) {
          r[e.subject.id] = e.subject;
          r[e.subject.id]["id_teacher"] = e.user.id;
          r[e.subject.id]["teacher_name"] = e.user.fullname;
          return r;
        }, {});
        }
      ));
  }

  deleteCourse(data: Course) {
    
  }

  createCourse(post: any) {
    
  }

  updateCourse(post: any) {
    
  }
}
