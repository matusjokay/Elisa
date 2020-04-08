import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth/auth.service';
import { FormControl, Validators } from '@angular/forms';
import { BaseService } from 'src/app/services/base-service.service';
import { TimetableService } from 'src/app/services/timetable.service';
import { SemesterVersion } from 'src/app/models/semester-version.model';

@Component({
  selector: 'app-version-select',
  templateUrl: './version-select.component.html',
  styleUrls: ['./version-select.component.less']
})
export class VersionSelectComponent implements OnInit {

  userName: string;
  versionsMap: SemesterVersion[];
  selectedVersion: SemesterVersion;
  selectedVersionControl: FormControl;

  constructor(private authService: AuthService,
    private router: Router,
    private baseService: BaseService,
    private timetableService: TimetableService) { }

  ngOnInit() {
    this.selectedVersionControl = new FormControl('', Validators.required);
    this.getUsername();
  }

  getUsername() {
    this.userName = this.baseService.getUserName();
    if (!this.userName) {
      this.authService.refreshToken().subscribe(
        (success) => {
          this.userName = this.baseService.getUserName();
          this.getVersions();
        },
        (error) => this.router.navigate(['login'])
      );
    } else {
      this.getVersions();
    }
  }

  getVersions() {
    this.timetableService.getAllSchemas().subscribe(
      (results: SemesterVersion[]) => {
        this.versionsMap = results;
      }
    );
  }

  onSelectionChanged(value: any) {
    console.log(value);
  }

  onProceed() {
    if (this.selectedVersionControl.valid && this.selectedVersionControl.value !== '') {
      this.selectedVersion = this.selectedVersionControl.value;
      localStorage.setItem('active_scheme', this.selectedVersion.name);
      this.router.navigateByUrl('/dashboard');
    } else {
      this.selectedVersionControl.setErrors({ required: true });
    }
  }

}
