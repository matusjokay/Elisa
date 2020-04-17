import { SemesterVersion } from './../models/semester-version.model';
import { Injectable } from '@angular/core';
import {environment} from '../../environments/environment';
import {map, share, distinctUntilChanged, shareReplay} from 'rxjs/operators';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import { BaseService } from './base-service.service';
import { Period } from '../models/period.model';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TimetableService {

  private cacheVersionList$: Observable<Array<SemesterVersion>>;

  constructor(private http: HttpClient,
    private baseService: BaseService) { }

  getActivitiesGroup(){
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});
    return this.http.get(environment.APIUrl + 'activity-categories/',options). //bude sa menit
    // pipe(timeout(20000),
    pipe(
      map((response: any) =>{
          let tmp = [];
          let language = localStorage.getItem('locale')
          for(let item of response){
            if(language === 'en'){
              item['name'] = item['name_en'];
            }
            else{
              item['name'] = item['name_sk'];
            }
          }
          return response;
        }
      ),share());
  }

  getAllEvents(version){
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.get(environment.APIUrl + 'timetables/'+ version + '/events/',options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ),share());
  }

  saveEvents(body,version){
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.post(environment.APIUrl + 'timetables/'+ version + '/events/',body,options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ),share());
  }

  updateEvent(body,version){
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.post(environment.APIUrl + 'timetables/'+ version + '/events/' + body.id + '/', body, options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ));
  }

  deleteEvent(version: number, id: string) {
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.delete(environment.APIUrl + 'timetables/'+ version + '/events/'+id+'/',options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ),share());
  }

  getAllCollisions(version){
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.get(environment.APIUrl + 'timetables/'+ version + '/collisions/',options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ),share());
  }


  saveCollision(body, version) {
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.post(environment.APIUrl + 'timetables/'+ version + '/collisions/',body,options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ),share());
  }

  getTimetableVersionLatest() {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.get(environment.APIUrl + 'timetables/latest/', { headers: httpOptions }).
    pipe(
      distinctUntilChanged(),
      share()
      );
  }

  getLastScheme() {
    const httpOptions = this.baseService.getAuthHeaderOnly();
    return this.http.get(environment.APIUrl + 'versions/latest/', { headers: httpOptions }).
    pipe(share());
  }

  createSchema(body){
    return this.http.post(environment.APIUrl + 'versions/', body).
    pipe(
      map((response: any) =>{
        localStorage.setItem('active_scheme',body['name']);
        return response;
        }
      ));
  }

  private requestAllSchemas(): Observable<SemesterVersion[]> {
    const httpOptions = this.baseService.getAuthHeaderOnly();
    return this.http.get<SemesterVersion[]>(environment.APIUrl + 'versions/',
      { headers: httpOptions });
  }

  getAllSchemas(clear?: boolean) {
    this.cacheVersionList$ = clear ? null : this.cacheVersionList$;
    if (!this.cacheVersionList$) {
      this.cacheVersionList$ = this.requestAllSchemas()
        .pipe(
          shareReplay(1)
        );
    }

    return this.cacheVersionList$;
  }

  createVersion(body){
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({ headers: headers });
    return this.http.post(environment.APIUrl + 'timetables/',
      body,
      options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ));
  }

  finalizeVersion(version) {
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({ headers: headers });

    let body = {};
    return this.http.post(environment.APIUrl + 'timetables/' + version + '/publish',
      body,
      options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ));
  }

  importByPeriod(versionName: string, periodId: number): Observable<any> {
    const httpOptions = this.baseService.getAuthHeaderOnly();
    return this.http.post(`${environment.APIUrl}versions/create_and_import/`,
      { name: versionName, period: periodId },
      { headers: httpOptions });
  }

  removeVersion(versionId: number): Observable<any> {
    const httpOptions = this.baseService.getAuthHeaderOnly();
    return this.http.delete(`${environment.APIUrl}versions/${versionId}`,
    { headers: httpOptions });
  }
}
