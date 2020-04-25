import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-spinner',
  templateUrl: './spinner.component.html',
  styleUrls: ['./spinner.component.less']
})
export class SpinnerComponent {

  @Input()
  public loadingText: string;
  @Input()
  public hidden: boolean;
  @Input()
  color = 'primary';
  mode = 'indeterminate';
  @Input()
  public diameter = 55;

  constructor() { }

}
