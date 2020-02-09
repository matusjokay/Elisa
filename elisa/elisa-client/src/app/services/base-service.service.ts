import { Injectable } from '@angular/core';
import { HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class BaseService {

  constructor() { }

  getSchemaHeader(): HttpHeaders {
    const token = localStorage.getItem('token');
    const version = localStorage.getItem('active_scheme');
    return new HttpHeaders({
        'Authorization': `Bearer ${token}`,
        'Timetable-Version': version
    });
  }

  getAuthHeaderOnly(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders({
        'Authorization': `Bearer ${token}`
    });
  }
}
