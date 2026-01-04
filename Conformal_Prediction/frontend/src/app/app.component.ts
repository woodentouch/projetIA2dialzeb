import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';

// Angular Material Modules
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSliderModule } from '@angular/material/slider';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { AmesData } from './ames-data.model';
import { PredictionService, PredictionInterval } from './prediction.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSliderModule,
    MatButtonModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  confidence: number = 95;
  lowerBound: number | null = null;
  upperBound: number | null = null;
  isFading: boolean = false;
  isLoading: boolean = false;
  predictionError: string | null = null;

  // Initialiser avec des valeurs par défaut raisonnables ou vides
  formData: AmesData = {
    'MS SubClass': 20,
    'MS Zoning': 'RL',
    'Lot Frontage': 80,
    'Lot Area': 9600,
    'Street': 'Pave',
    'Alley': null,
    'Lot Shape': 'Reg',
    'Land Contour': 'Lvl',
    'Utilities': 'AllPub',
    'Lot Config': 'Inside',
    'Land Slope': 'Gtl',
    'Neighborhood': 'NAmes',
    'Condition 1': 'Norm',
    'Condition 2': 'Norm',
    'Bldg Type': '1Fam',
    'House Style': '1Story',
    'Overall Qual': 6,
    'Overall Cond': 5,
    'Year Built': 1970,
    'Year Remod/Add': 1970,
    'Roof Style': 'Gable',
    'Roof Matl': 'CompShg',
    'Exterior 1st': 'HdBoard',
    'Exterior 2nd': 'HdBoard',
    'Mas Vnr Type': 'None',
    'Mas Vnr Area': 0,
    'Exter Qual': 'TA',
    'Exter Cond': 'TA',
    'Foundation': 'CBlock',
    'Bsmt Qual': 'TA',
    'Bsmt Cond': 'TA',
    'Bsmt Exposure': 'No',
    'BsmtFin Type 1': 'ALQ',
    'BsmtFin SF 1': 978,
    'BsmtFin Type 2': 'Unf',
    'BsmtFin SF 2': 0,
    'Bsmt Unf SF': 284,
    'Total Bsmt SF': 1262,
    'Heating': 'GasA',
    'Heating QC': 'Ex',
    'Central Air': 'Y',
    'Electrical': 'SBrkr',
    '1st Flr SF': 1262,
    '2nd Flr SF': 0,
    'Low Qual Fin SF': 0,
    'Gr Liv Area': 1262,
    'Bsmt Full Bath': 0,
    'Bsmt Half Bath': 1,
    'Full Bath': 2,
    'Half Bath': 0,
    'Bedroom AbvGr': 3,
    'Kitchen AbvGr': 1,
    'Kitchen Qual': 'TA',
    'TotRms AbvGrd': 6,
    'Functional': 'Typ',
    'Fireplaces': 1,
    'Fireplace Qu': 'TA',
    'Garage Type': 'Attchd',
    'Garage Yr Blt': 1976,
    'Garage Finish': 'RFn',
    'Garage Cars': 2,
    'Garage Area': 460,
    'Garage Qual': 'TA',
    'Garage Cond': 'TA',
    'Paved Drive': 'Y',
    'Wood Deck SF': 298,
    'Open Porch SF': 0,
    'Enclosed Porch': 0,
    '3Ssn Porch': 0,
    'Screen Porch': 0,
    'Pool Area': 0,
    'Pool QC': null,
    'Fence': null,
    'Misc Feature': null,
    'Misc Val': 0,
    'Mo Sold': 5,
    'Yr Sold': 2007,
    'Sale Type': 'WD',
    'Sale Condition': 'Normal'
  };

  // Liste des features pour générer le formulaire, excluant les identifiants et la cible
  allFeatures: (keyof AmesData)[] = Object.keys(this.formData) as (keyof AmesData)[];

  numericFields: (keyof AmesData)[] = [
    'Lot Frontage', 'Lot Area', 'Overall Qual', 'Overall Cond', 'Year Built', 'Year Remod/Add',
    'Mas Vnr Area', 'BsmtFin SF 1', 'BsmtFin SF 2', 'Bsmt Unf SF', 'Total Bsmt SF',
    '1st Flr SF', '2nd Flr SF', 'Low Qual Fin SF', 'Gr Liv Area', 'Bsmt Full Bath',
    'Bsmt Half Bath', 'Full Bath', 'Half Bath', 'Bedroom AbvGr', 'Kitchen AbvGr',
    'TotRms AbvGrd', 'Fireplaces', 'Garage Yr Blt', 'Garage Cars', 'Garage Area',
    'Wood Deck SF', 'Open Porch SF', 'Enclosed Porch', '3Ssn Porch', 'Screen Porch',
    'Pool Area', 'Misc Val', 'Mo Sold', 'Yr Sold'
  ];

  constructor(private predictionService: PredictionService) {}

  isNumeric(field: keyof AmesData): boolean {
    return this.numericFields.includes(field);
  }

  onSubmit(): void {
    this.isLoading = true;
    this.isFading = true;
    this.predictionError = null;
    this.lowerBound = null;
    this.upperBound = null;

    // Convertir les valeurs vides en null
    const features: any = { ...this.formData };
    for (const key in features) {
      if (features[key] === '' || features[key] === undefined) {
        features[key] = null;
      }
    }
    
    // L'alpha est 1 - (niveau de confiance / 100)
    const alpha = 1 - (this.confidence / 100);

    this.predictionService.predict(features, alpha).subscribe({
      next: (result: PredictionInterval) => {
        this.lowerBound = result.lower;
        this.upperBound = result.upper;
        this.isLoading = false;
        setTimeout(() => { this.isFading = false; }, 50);
      },
      error: (err) => {
        console.error('Erreur lors de la prédiction:', err);
        this.predictionError = 'Une erreur est survenue lors de la communication avec le serveur. Vérifiez la console pour plus de détails.';
        this.isLoading = false;
        this.isFading = false;
      }
    });
  }
}
