import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { DevicesPageComponent } from './devices-page/devices-page.component';
import { DeviceRecordingsPageComponent } from './device-recordings-page/device-recordings-page.component';

const routes: Routes = [
  { path: '', redirectTo: 'devices', pathMatch: 'full' },
  { path: 'devices', component: DevicesPageComponent },
  { path: 'devices/:id/recordings', component: DeviceRecordingsPageComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
