import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  MatAutocompleteModule,
  MatButtonModule, MatButtonToggleModule, MatCardModule, MatDialogModule,
  MatExpansionModule,
  MatFormFieldModule, MatGridListModule,
  MatIconModule,
  MatInputModule,
  MatListModule, MatMenuModule, MatPaginatorModule, MatSelectModule,
  MatSidenavModule, MatSlideToggleModule, MatSortModule, MatTableModule, MatTabsModule, MatToolbarModule, MatTreeModule
} from '@angular/material';
import {FlexLayoutModule} from '@angular/flex-layout';
import {LayoutModule} from '@angular/cdk/layout';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';


@NgModule({
  imports: [
    CommonModule,
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    MatExpansionModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatCardModule,
    MatGridListModule,
    MatMenuModule,
    LayoutModule,
    MatToolbarModule,
    FlexLayoutModule,
    BrowserAnimationsModule,
    MatTableModule,
    MatAutocompleteModule,
    MatTreeModule,
    MatSelectModule,
    MatDialogModule,
    MatButtonToggleModule,
    MatSlideToggleModule,
    MatTabsModule,
    MatSortModule,
    MatPaginatorModule
  ],
  exports:[
    CommonModule,
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    MatExpansionModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatCardModule,
    MatGridListModule,
    MatMenuModule,
    LayoutModule,
    MatToolbarModule,
    FlexLayoutModule,
    BrowserAnimationsModule,
    MatTableModule,
    MatAutocompleteModule,
    MatTreeModule,
    MatSelectModule,
    MatDialogModule,
    MatButtonToggleModule,
    MatSlideToggleModule,
    MatTabsModule,
    MatSortModule,
    MatPaginatorModule,
  ],
  declarations: [
  ]
})
export class MaterialModule { }
