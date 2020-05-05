import { Component, OnInit, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-confirm-dialog',
  templateUrl: './confirm-dialog.component.html',
  styleUrls: ['./confirm-dialog.component.less']
})
export class ConfirmDialogComponent implements OnInit {

  isSimpleDialog: boolean;
  message: string;

  constructor(
    public dialogRef: MatDialogRef<ConfirmDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: {msg: string, isSimple: boolean}) { }

    ngOnInit(): void {
      this.message = this.data.msg;
      this.isSimpleDialog = this.data.isSimple;
    }

    onNoClick(): void {
      this.dialogRef.close(false);
    }
}
