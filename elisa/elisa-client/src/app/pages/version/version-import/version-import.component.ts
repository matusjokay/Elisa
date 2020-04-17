import { TimetableService } from './../../../services/timetable.service';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { SnackbarComponent } from './../../../common/snackbar/snackbar.component';
import { PeriodService } from './../../../services/period.service';
import { Component, OnInit, Inject } from '@angular/core';
import { Period } from 'src/app/models/period.model';

@Component({
  selector: 'app-version-import',
  templateUrl: './version-import.component.html',
  styleUrls: ['./version-import.component.less']
})
export class VersionImportComponent implements OnInit {

  academicPeriods: Period[];
  selectedPeriod: Period;
  importedPeriodIds: number[];
  customVersion = false;
  import: boolean;
  importing: boolean;
  academicPeriodsGrouped: { year: string, periods: Period[]}[];
  spinnerText: string;
  loading: boolean;

  constructor(private periodService: PeriodService,
    private timetableService: TimetableService,
    private snackbar: SnackbarComponent,
    private dialogRef: MatDialogRef<VersionImportComponent>,
    @Inject(MAT_DIALOG_DATA) public dialogData: any) { }

  ngOnInit(): void {
    this.importedPeriodIds = this.dialogData;
    this.fetchAllPeriods();
  }

  fetchAllPeriods() {
    this.onRequestSent('Fetching periods...');
    this.periodService.getAllPeriods().subscribe(
      (success) => {
        success = this.defineYear(success);
        let grouped = this.groupPeriodsByAcademicSequence(success);
        grouped = this.sortPeriods(grouped);
        this.academicPeriodsGrouped = grouped.map(periods => {
          return { year: periods[0]['year'], periods: periods };
        });
      },
      (error) => {
        console.error(error);
        this.snackbar.openSnackBar(
          'Failed to fetch periods!',
          'Close',
          this.snackbar.styles.failure);
        this.dialogRef.close(false);
      }
    ).add(
      this.onRequestDone()
    );
  }

  defineYear(results: Period[]): Period[] {
    return results.map(period => ({ ...period, year: period.name.match(/^(.)*(\d{4}\/\d{4})(.)*$/)[2]}));
  }

  groupPeriodsByAcademicSequence(periods: Period[]): Array<any[]> {
    const groupBy = (data, key) => { // `data` is an array of objects, `key` is the key (or property accessor) to group by
    // reduce runs this anonymous function on each element of `data` (the `item` parameter,
    // returning the `storage` parameter at the end
      return data.reduce((storage, item) => {
        // get the first instance of the key by which we're grouping
        const group = item[key];
        // set `storage` for this instance of group to the outer scope (if not empty) or initialize it
        storage[group] = storage[group] || [];
        // add this item to its group within `storage`
        storage[group].push(item);
        // return the updated storage to the reduce function, which will then loop through the next 
        return storage;
      }, {}); // {} is the initial value of the storage
    };
    let resultArray = groupBy(periods, 'university_period');
    console.log('result Array');
    console.log(resultArray);
    // transform it to an array
    resultArray = Object.values(resultArray);
    return resultArray;
  }

  sortPeriods(arr: Array<Period[]>) {
    // sort the values descendingly
    return arr.sort((a: Period[], b: Period[]) => a[0].university_period > b[0].university_period ? -1 :
      a[0].university_period < b[0].university_period ? 1 : 0);
  }

  onImportVersion() {
    const versionName = this.prepareNameForImport(this.selectedPeriod.name);
    const periodId = this.selectedPeriod.id;
    this.onRequestSent('Importing data for selected period...<br>This will take a while please wait...',
      true);
    this.timetableService.importByPeriod(versionName, periodId).subscribe(
      (success) => {
        this.snackbar.openSnackBar(`Successfully imported data by period -> ${this.selectedPeriod.name}`,
        'Close',
        this.snackbar.styles.success);
        this.dialogRef.close(true);
      },
      (error) => {
        console.error(error);
        this.snackbar.openSnackBar(
          'Failed to import data!',
          'Close',
          this.snackbar.styles.failure,
          true);
      }
    ).add(() => {
      this.onRequestDone();
    });
  }

  prepareNameForImport(periodName: string): string {
    return periodName.split(/[\s\/]+/).join('_');
  }

  onRequestSent(msg: string, isImport?: boolean) {
    this.spinnerText = msg;
    this.loading = true;
    this.importing = isImport ? true : false;
  }

  onRequestDone() {
    this.spinnerText = '';
    this.loading = false;
  }

  onClose() {
    this.dialogRef.close(false);
  }

}
