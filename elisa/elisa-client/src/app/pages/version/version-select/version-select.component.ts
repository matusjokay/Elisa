import { RoleAuth, RoleManager } from './../../../models/role.model';
import { SnackbarComponent } from './../../../common/snackbar/snackbar.component';
import { MatSelectChange } from '@angular/material/select';
import { MatDialog } from '@angular/material/dialog';
import { VersionImportComponent } from './../version-import/version-import.component';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth/auth.service';
import { FormControl, Validators } from '@angular/forms';
import { BaseService } from 'src/app/services/base-service.service';
import { TimetableService } from 'src/app/services/timetable.service';
import { SemesterVersion } from 'src/app/models/semester-version.model';
import { tap } from 'rxjs/operators';
import { ConfirmDialogComponent } from 'src/app/common/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-version-select',
  templateUrl: './version-select.component.html',
  styleUrls: ['./version-select.component.less']
})
export class VersionSelectComponent implements OnInit {

  userName: string;
  versionsMap: SemesterVersion[];
  lastUpdated: Date;
  deleteFailedVersion: boolean;
  selectedVersion: SemesterVersion;
  selectedVersionControl: FormControl;
  authorization: RoleAuth;
  empty: boolean;
  spinnerText: string;
  loading: boolean;
  selected: boolean;
  importedVersionsByPeriod: number[];

  constructor(private authService: AuthService,
    private router: Router,
    private baseService: BaseService,
    private timetableService: TimetableService,
    private snackbar: SnackbarComponent,
    private dialog: MatDialog) { }

  ngOnInit() {
    this.selectedVersionControl = new FormControl('', Validators.required);
    this.userName = this.baseService.getUserName();
    this.authorization = RoleManager.getRolePrivileges(this.baseService.getUserRoles());
    this.getInfoAboutData();
  }

  getInfoAboutData() {
    this.timetableService.getPublicSchema().subscribe(
      (success) => {
        if (success.last_updated) {
          this.lastUpdated = new Date(success.last_updated);
        }
      },
      (error) => {
        console.error(error);
        this.snackbar.openSnackBar(
          'Failed to fetch basic public version! SERVER ISSUE!',
          'Close',
          this.snackbar.styles.failure);
      }
    ).add(() => this.getVersions());
  }

  getVersions(clear?: boolean) {
    this.onRequestSent('Fetching imported versions...');
    this.timetableService.getAllSchemas(clear)
      .pipe(tap(() => this.onRequestDone()))
      .subscribe(
      (results: SemesterVersion[]) => {
        this.versionsMap = results;
        this.importedVersionsByPeriod = this.versionsMap.map(version => version.period);
        this.empty = this.versionsMap && this.versionsMap.length > 0 ? false : true;
      },
      (error) => {
        console.error(error);
        this.snackbar.openSnackBar(
          'Failed to fetch versions!',
          'Close',
          this.snackbar.styles.failure);
      }
    );
  }

  onSelectionChanged(change: MatSelectChange) {
    if (this.selectedVersionControl.valid &&
      (this.selectedVersionControl.value !== ''
      || this.selectedVersionControl.value)) {
      this.selected = true;
      this.selectedVersion = change.value;
    } else {
      this.selected = false;
      delete this.selectedVersion;
    }
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

  onImport() {
    const dialogRef = this.dialog.open(
      VersionImportComponent,
      { height: '60vh',
        width: '50vw',
        disableClose: true,
        data: this.importedVersionsByPeriod
      });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        if (result['id'] && result['name']) {
          this.onDeleteVersion(result['id'], result['name']);
        } else {
          this.getVersions(true);
        }
      }
    });
  }

  onDeleteVersion(failedId?: number, failedName?: string) {
    const versionId = !failedId ? this.selectedVersion.id : failedId;
    const name = !failedName ? this.selectedVersion.name : failedName;
    this.onRequestSent(`Removing ${name}...`);
    this.timetableService.removeVersion(versionId).subscribe(
      (success) => this.snackbar.openSnackBar(
        `Successfully deleted version -> ${name}`,
        'Close',
        this.snackbar.styles.success),
      (error) => {
        this.snackbar.openSnackBar(
        'Failed to delete version!',
        'Close',
        this.snackbar.styles.failure);
      }).add(() => {
        this.onRequestDone();
        delete this.selectedVersion;
        this.selected = false;
        this.getVersions(true);
      });
  }

  performImportOfInitData() {
    console.log('importing');
    this.onRequestSent('Performing Import of the latest data');
    this.timetableService.importInitData().subscribe(
      (success) => {
        this.snackbar.openSnackBar(
          `Successfully Inserted / Updated Data!`,
          'Close',
          this.snackbar.styles.success),
        setTimeout(() => {
          this.onRequestSent('Data updated! Logging out...');
          this.logout();
        }, 1000);
      },
      (error) => {
        this.snackbar.openSnackBar(
          'Failed to insert/update data!',
          'Close',
          this.snackbar.styles.failure);
      }
    ).add(() => this.onRequestDone());
  }

  onDataRefresh() {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '25%',
      data: `This will <b>insert/update</b> the most recent data for :<br>
      <ul>
        <li>Users</li>
        <li>Periods</li>
        <li>Departments</li>
      </ul><br><br>
      After that you'll be logged out.<br>
      This is to make sure data is displayed correctly<br><br>
      It may take some time... <br>
      <b>Continue?</b>`
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.performImportOfInitData();
      }
    });
  }

  onRequestSent(msg?: string) {
    this.spinnerText = msg;
    this.loading = true;
  }

  onRequestDone() {
    this.spinnerText = '';
    this.loading = false;
  }

  logout() {
    this.onRequestSent('Logging out...');
    this.authService.logout().subscribe(
      (success) => {
        this.router.navigate(['login']);
      }
    ).add(() => this.onRequestDone());
  }

}
