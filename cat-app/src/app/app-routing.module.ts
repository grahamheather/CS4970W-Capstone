import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { DevicesPageComponent } from './devices-page/devices-page.component';

const routes: Routes = [
  { path: 'devices', component: DevicesPageComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
