import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home.component';
import { SimulationComponent } from './pages/simulation/simulation.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'simulation', component: SimulationComponent },
  { path: '**', redirectTo: '' },
];
