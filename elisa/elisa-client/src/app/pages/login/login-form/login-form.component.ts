import {Component, OnInit, OnDestroy} from '@angular/core';
import {User} from '../../../models/user';
import {HttpClient } from '@angular/common/http';
import {AuthService} from '../../../services/auth/auth.service';
import {Subscription} from 'rxjs';
import {FormControl, FormGroup, Validators, FormGroupDirective} from '@angular/forms';
import {Router} from '@angular/router';
import {Account} from '../../../models/account.model';
import { catchError } from 'rxjs/operators';
import { MyErrorStateMatcher } from 'src/app/common/form-error-state';
import { SnackbarComponent } from 'src/app/common/snackbar/snackbar.component';
import { ErrorMessageCreator } from 'src/app/common/error-message';

@Component({
  selector: 'app-login-form',
  templateUrl: './login-form.component.html',
  styleUrls: ['./login-form.component.less']
})
export class LoginFormComponent implements OnInit, OnDestroy {
  account = new Account();
  response: Subscription;
  loginForm: FormGroup;
  matcher = new MyErrorStateMatcher();
  errorMessageCreator = new ErrorMessageCreator();
  loading = false;
  statusText: string;

  constructor(private httpClient: HttpClient,
              private authService: AuthService,
              private router: Router,
              private snackBar: SnackbarComponent
  ) {}

  ngOnInit(): void {
    this.loginForm = new FormGroup({
      'name': new FormControl(this.account.username, [
        Validators.required,
      ]),
      'password': new FormControl(this.account.password, [
        Validators.required,
      ])
    });
  }

  get name() { return this.account.username; }

  get password() { return this.account.password; }

  onSubmit() {
    this.account.username = this.loginForm.value.name;
    this.account.password = this.loginForm.value.password;
    this.onRequestSent('Submitting login credentials');
    this.response = this.authService.login(this.account).subscribe(
      (response: any) => {
        this.router.navigateByUrl('/admin');
        // return response['token'];
      }, (error) => {
        console.error('login failed');
        const msg = this.errorMessageCreator.createStringMessage(error);
        this.snackBar.openSnackBar(msg, 'Close', 'red-snackbar');
        catchError(error);
      }
    ).add(() => {
      this.onRequestDone();
    });
  }

  get diagnostic() { return JSON.stringify(this.account); }

  onRequestSent(text?: string) {
    this.loading = true;
    this.statusText = text;
  }

  onRequestDone() {
    this.loading = false;
    this.statusText = '';
  }

  ngOnDestroy() {
    this.response.unsubscribe();
  }

}
