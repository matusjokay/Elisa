import { UserRoleService } from 'src/app/services/auth/user-role.service';
import { BaseService } from 'src/app/services/base-service.service';
import { Component, OnInit, OnDestroy } from '@angular/core';
import { AuthService } from '../../../services/auth/auth.service';
import { Subscription } from 'rxjs';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { Account } from '../../../models/account.model';
import { catchError } from 'rxjs/operators';
import { MyErrorStateMatcher } from 'src/app/common/form-error-state';
import { SnackbarComponent } from 'src/app/common/snackbar/snackbar.component';
import { ErrorMessageCreator } from 'src/app/common/error-message';
import * as _ from 'lodash';
import * as Globals from '../../../models/globals';

@Component({
  selector: 'app-login-form',
  templateUrl: './login-form.component.html',
  styleUrls: ['./login-form.component.less']
})
export class LoginFormComponent implements OnInit {
  account = new Account();
  response: Subscription;
  loginForm: FormGroup;
  matcher = new MyErrorStateMatcher();
  errorMessageCreator = new ErrorMessageCreator();
  loading: boolean;
  hidePwd = true;
  statusText: string;
  redirectUrl: string;

  constructor(private authService: AuthService,
              private baseService: BaseService,
              private userRoleService: UserRoleService,
              private router: Router,
              private route: ActivatedRoute,
              private snackBar: SnackbarComponent
  ) {}

  ngOnInit(): void {
    // fetch parameters when refresh token expires
    // and return to where you were previously
    this.route.queryParams.subscribe(
      (result) => {
        if (!_.isEmpty(result) &&
            !Globals.getUrlRedirect()) {
          Globals.setUrlRedirect(result['urlRedirect']);
        }
      }
    );
    this.loginForm = new FormGroup({
      'name': new FormControl(this.account.username, [
        Validators.required,
      ]),
      'password': new FormControl(this.account.password, [
        Validators.required,
      ])
    });
  }

  onSubmit() {
    this.onRequestSent('Submitting login credentials');
    this.account.username = this.loginForm.value.name;
    this.account.password = this.loginForm.value.password;
    this.authService.login(this.account)
      .subscribe(
      (response: any) => {
        this.onRequestSent('Loggin Successful<br>Checking roles for user...');
        this.afterLoginRoleInit();
      }, (error) => {
        console.error('login failed');
        this.onRequestDone();
        const msg = this.errorMessageCreator.createStringMessage(error);
        this.snackBar.openSnackBar(msg, 'Close', this.snackBar.styles.failure);
        catchError(error);
      }
    );
  }

  afterLoginRoleInit() {
    const userId = this.baseService.getUserId();
    this.userRoleService.setInitUserRoles(this.account, userId)
      .subscribe(
        (success) => {
          if (success === 'OK') {
            this.statusText = 'Roles Fetched!';
          } else {
            const msg = success['default'] ? 'Default roles set!' : 'Admin roles set!';
            this.snackBar.openSnackBar(
              msg,
              'Close',
              this.snackBar.styles.success,
              true
            );
          }
          setTimeout(() => {
            let url = Globals.getUrlRedirect();
            url = url === '/' || url === '/login' ? null : url;
            Globals.setUrlRedirect('');
            if (url && localStorage.getItem('active_scheme')) {
              this.router.navigateByUrl(url);
            } else if (!url && localStorage.getItem('active_scheme')) {
              this.router.navigateByUrl('/dashboard');
            } else {
              this.router.navigateByUrl('/version-select');
            }
          }, 700);
        },
        (error) => {
          console.error('login failed');
          const msg = this.errorMessageCreator.createStringMessage(error);
          this.snackBar.openSnackBar(msg, 'Close', 'red-snackbar');
          catchError(error);
        }
      ).add(() => this.onRequestDone());
  }

  onRequestSent(text?: string) {
    this.loading = true;
    this.statusText = text;
  }

  onRequestDone() {
    this.loading = false;
    this.statusText = '';
  }

}
