import {Component, OnInit} from '@angular/core';
import {User} from '../../../models/user';
import {HttpClient } from '@angular/common/http';
import {AuthService} from '../../../services/auth/auth.service';
import {Subscription} from 'rxjs';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {Router} from '@angular/router';
import {Account} from '../../../models/account.model';

@Component({
  selector: 'app-login-form',
  templateUrl: './login-form.component.html',
  styleUrls: ['./login-form.component.less']
})
export class LoginFormComponent implements OnInit{
  account = new Account();
  response: Subscription;
  loginForm: FormGroup;

  constructor(private httpClient: HttpClient,
              private authService: AuthService,
              private router: Router,
  ){}

  ngOnInit(): void{
    this.loginForm = new FormGroup({
      'name': new FormControl(this.account.username,[
        Validators.required,
      ]),
      'password': new FormControl(this.account.password,[
        Validators.required,
      ])
    });
  }

  get name() { return this.account.username; }

  get password() { return this.account.password; }

  onSubmit() {
    this.account.username = this.loginForm.value.name;
    this.account.password = this.loginForm.value.password;

    this.response = this.authService.login(this.account).subscribe(
      (response: any) => {
        this.router.navigateByUrl("/admin");
        return response['token'];
      }
    );
    if(this.response){

    }
  }

  get diagnostic() { return JSON.stringify(this.account); }

}
