import { Injectable } from '@angular/core';
import {Observable} from 'rxjs';
import {environment} from '../../environments/environment';
import {map, share, distinctUntilChanged} from 'rxjs/operators';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {Course} from '../models/course';
import { IPage } from '../models/page.model';
import { BaseService } from './base-service.service';

@Injectable({
  providedIn: 'root'
})
export class CourseService {

  constructor(private http: HttpClient,
    private baseService: BaseService) { }

  getAll(pageNum: number, pageSize: number): Observable<IPage> {
    const httpParams = new HttpParams()
      .set('page', pageNum.toString())
      .set('page_size', pageSize.toString());
    const httpOptions = this.baseService.getSchemaHeader();

    return this.http.get<IPage>(environment.APIUrl + 'courses/', { params: httpParams, headers : httpOptions }).pipe(
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

  deleteCourse(courseId: number) {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.delete(environment.APIUrl + `courses/${courseId}/`, { headers: httpOptions });
  }

  createCourse(newCourse: Course) {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.post<Course>(environment.APIUrl + 'courses/', newCourse, { headers: httpOptions });
  }

  updateCourse(updatedCourse: Course) {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.put<Course>(environment.APIUrl + `courses/${updatedCourse.id}/`, updatedCourse, { headers : httpOptions });
  }
}
