import { AsyncPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { combineLatest } from 'rxjs';
import { MatchPrediction, MatchState } from '../../models/worldcup.models';
import { PredictionService } from '../../services/prediction.service';
import { ResponsibleNoticeComponent } from '../../components/responsible-notice/responsible-notice.component';
import { WorldCupService } from '../../services/worldcup.service';
import { GroupTabsComponent } from '../../components/group-tabs/group-tabs.component';
import { MatchModalComponent } from '../../components/match-modal/match-modal.component';

@Component({
  selector: 'app-home',
  imports: [
    AsyncPipe,
    GroupTabsComponent,
    MatchModalComponent,
    ResponsibleNoticeComponent,
    RouterLink,
  ],
  templateUrl: './home.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomeComponent {
  private readonly predictionService = inject(PredictionService);
  private readonly worldCupService = inject(WorldCupService);

  readonly selectedMatchId = signal<string | null>(null);
  readonly viewModel$ = combineLatest({
    predictions: this.predictionService.getPredictions(),
    eloPredictions: this.predictionService.getEloPredictions(),
    groups: this.worldCupService.getGroups(),
    groupStrengths: this.worldCupService.getStrengths(),
    matchStates: this.worldCupService.getMatchStates(),
    liveStandings: this.worldCupService.getLiveGroupStandings(),
    referenceOdds: this.worldCupService.getMatchReferenceOddsV2231(),
  });

  predictionFor(predictions: MatchPrediction[], matchId: string): MatchPrediction | undefined {
    return predictions.find((prediction) => prediction.matchId === matchId);
  }

  matchStateFor(states: MatchState[], matchId: string): MatchState | undefined {
    return states.find((state) => state.matchId === matchId);
  }

  referenceOddsFor(payload: any, matchId: string): any {
    return payload?.fixtures?.find((fixture: any) => fixture.match_id === matchId);
  }

}
