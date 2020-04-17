import { Component, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-snackbar',
  templateUrl: './snackbar.component.html',
  styleUrls: ['./snackbar.component.less']
})
export class SnackbarComponent {

  public styles = {
    success: 'blue-snackbar',
    failure: 'red-snackbar'
  };

  private duration = 3500;

  constructor(public snackBar: MatSnackBar) { }

  openSnackBar(message: string, action: string, className: string, infinite?: boolean) {
    this.snackBar.open(message, action, {
      duration: infinite ? undefined : this.duration,
      verticalPosition: 'bottom',
      horizontalPosition: 'right',
      panelClass: [className]
    });
  }

}
