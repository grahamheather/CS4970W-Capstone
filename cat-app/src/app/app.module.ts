import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { DevicesPageComponent } from './devices-page/devices-page.component';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { MatBottomSheetModule } from '@angular/material/bottom-sheet';
import { AddDeviceSheetComponent } from './add-device-sheet/add-device-sheet.component';
import { DevicesService } from './services/devices.service';
import { HttpClientModule } from '@angular/common/http';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule, NG_VALIDATORS } from '@angular/forms';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatMomentDateModule, MAT_MOMENT_DATE_ADAPTER_OPTIONS } from '@angular/material-moment-adapter';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSliderModule } from '@angular/material/slider';
import { GreaterThanValidator } from './validators/greater-than-validator';
import { IntegerValidator } from './validators/integer-validator';
import { FloatValidator } from './validators/float-validator';
import { MatSelectModule } from '@angular/material/select';
import { DeviceComponent } from './device/device.component';
import { DeviceEditComponent } from './device-edit/device-edit.component';
import { DeviceSettingsComponent } from './device-settings/device-settings.component';
import { DeviceSettingsEditComponent } from './device-settings-edit/device-settings-edit.component';
import { DeviceRecordingsPageComponent } from './device-recordings-page/device-recordings-page.component';
import { RecordingsService } from './services/recordings.service';
import { MatTableModule } from '@angular/material/table';

@NgModule({
  declarations: [
    AppComponent,
    DevicesPageComponent,
    AddDeviceSheetComponent,
    GreaterThanValidator,
    IntegerValidator,
    FloatValidator,
    DeviceComponent,
    DeviceEditComponent,
    DeviceSettingsComponent,
    DeviceSettingsEditComponent,
    DeviceRecordingsPageComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MatToolbarModule,
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatListModule,
    MatMenuModule,
    MatBottomSheetModule,
    HttpClientModule,
    MatDividerModule,
    MatFormFieldModule,
    MatInputModule,
    FormsModule,
    MatDatepickerModule,
    MatMomentDateModule,
    MatProgressBarModule,
    MatTooltipModule,
    MatExpansionModule,
    MatSlideToggleModule,
    MatSliderModule,
    MatSelectModule,
    MatTableModule
  ],
  entryComponents: [
    AddDeviceSheetComponent
  ],
  providers: [
    DevicesService,
    { provide: MAT_MOMENT_DATE_ADAPTER_OPTIONS, useValue: { useUtc: true } },
    RecordingsService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
