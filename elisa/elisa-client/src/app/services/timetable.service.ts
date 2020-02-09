import { Injectable } from '@angular/core';
import {environment} from '../../environments/environment';
import {map, share, timeout, distinctUntilChanged, shareReplay} from 'rxjs/operators';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import { BaseService } from './base-service.service';
import { Period } from '../models/period.model';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TimetableService extends BaseService {

  private cachePeriodList$: Observable<Array<Period>>;

  constructor(private http: HttpClient) {
    super();
  }

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
    const token = localStorage.getItem('token');
    const version = localStorage.getItem('active_scheme');
    const httpOptions = {
      headers: new HttpHeaders({
        'Authorization': `Bearer ${token}`,
        'Timetable-Version': version
      })
    };

    return this.http.get(environment.APIUrl + 'timetables/latest/', httpOptions).
    pipe(
      distinctUntilChanged(),
      share()
      );
  }

  getLastScheme() {
    // const httpHeaders = new HttpHeaders();
    // httpHeaders.append('Authorization', `Bearer ${localStorage.getItem('token')}`);
    const token = localStorage.getItem('token');
    const httpOptions = {
      headers: new HttpHeaders({
        'Authorization': `Bearer ${token}`
      })
    };
    // map is probably redundant
    return this.http.get(environment.APIUrl + 'versions/latest/', httpOptions).
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

  getAllSchemas() {
    const token = localStorage.getItem('token');
    const httpOptions = {
      headers: new HttpHeaders({
        'Authorization': `Bearer ${token}`
      })
    };
    return this.http.get(environment.APIUrl + 'versions/', httpOptions).
    pipe(share());
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

  getCurrentSelectedPeriods() {
    if (!this.cachePeriodList$) {
      this.cachePeriodList$ = this.requestPeriods().pipe(
        shareReplay(1)
      );
    }

    return this.cachePeriodList$;
  }

  private requestPeriods(): Observable<Period[]> {
    const httpOptions = this.getSchemaHeader();
    return this.http.get<Period[]>(environment.APIUrl + 'periods/current/', { headers: httpOptions });
  }
}
