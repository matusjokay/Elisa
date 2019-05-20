import { Injectable } from '@angular/core';
import {environment} from '../../environments/environment';
import {map, timeout} from 'rxjs/operators';
import {HttpClient, HttpHeaders} from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class TimetableService {

  constructor(private http: HttpClient) { }

  getActivitiesGroup(){
    return this.http.get(environment.APIUrl + 'activity-categories/'). //bude sa menit
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
      ));
  }

  getAllEvents(version){
    return this.http.get(environment.APIUrl + 'timetables/'+ version + '/events/').
    pipe(
      map((response: any) =>{
          return response;
        }
      ));
  }

  getAllCollisions(version){
    return this.http.get(environment.APIUrl + 'timetables/'+ version + '/collisions/').
    pipe(
      map((response: any) =>{
          return response;
        }
      ));
  }

  getTimetableVersions(version){
    return this.http.get(environment.APIUrl + 'timetables/').
    pipe(
      map((response: any) =>{
          return response;
        }
      ));
  }

  getLastScheme(){
    return this.http.get(environment.APIUrl + 'version-latest/').
    pipe(
      map((response: any) =>{
          return response;
        }
      ));
  }

  createSchema(body){
    return this.http.post(environment.APIUrl + 'versions/', body).
    pipe(
      map((response: any) =>{
        localStorage.setItem('schema',body['name']);
        return response;
        }
      ));
  }

  getAllSchemas(){
    return this.http.get(environment.APIUrl + 'versions/').
    pipe(
      map((response: any) =>{
          return response;
        }
      ));
  }

  createVersion(body){
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('HTTP_TIMETABLE_VERSION', localStorage.getItem('schema'));
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
}
