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
    this.getVersions();
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
        this.getVersions(true);
      }
    });
  }

  onDeleteVersion() {
    const versionId = this.selectedVersion.id;
    const name = this.selectedVersion.name;
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
