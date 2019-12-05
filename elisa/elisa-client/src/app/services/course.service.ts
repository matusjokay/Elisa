import { Injectable } from '@angular/core';
import {Observable} from 'rxjs';
import {environment} from '../../environments/environment';
import {map, share, distinctUntilChanged} from 'rxjs/operators';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {Course} from '../models/course';

@Injectable({
  providedIn: 'root'
})
export class CourseService {

  constructor(private http: HttpClient) { }

  getAll(): Observable<Course[]> {
    const token = localStorage.getItem('token');
    const version = localStorage.getItem('active_scheme');
    const httpOptions = {
      headers: new HttpHeaders({
        'Authorization': `Bearer ${token}`,
        'Timetable-Version': version
      })
    };

    return this.http.get<Course[]>(environment.APIUrl + 'courses/', httpOptions).pipe(
      distinctUntilChanged(),
      share()
      );
  }

  getCoursesByTeacherMap(): Observable<Course[]>{
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.get<Course[]>(environment.APIUrl + "teachers/", options).pipe(
      map((response: any) => {
        return response.reduce(function(r, e) {
          r[e.subject.id] = e.subject;
          r[e.subject.id]["id_teacher"] = e.user.id;
          r[e.subject.id]["teacher_name"] = e.user.fullname;
          return r;
        });
        }
      ),
      share());
  }

  deleteCourse(data: Course) {

  }

  createCourse(post: any) {

  }

  updateCourse(post: any) {

  }
}
