# CBT Cards mobile privacy reconciliation audit

Status: **implementation verification pending**

Public store metadata rechecked: **19 August 2026**

Implementation-policy baseline: **14 July 2026**

This file records the difference between the CBT Cards website privacy policy, observable public store disclosures, and the implementation evidence that still has to be checked before those disclosures can be called reconciled. It does not treat a store label as proof of application behavior and it does not infer private journal-content handling from a broad store category.

## Known implementation-policy baseline

The privacy policy written from the implementation audit on 14 July 2026 records these boundaries:

- settings, card state, diary entries, check-ins, notes, reminders, activity history, and supported tool entries are stored locally in Hive;
- supported Hive boxes attempt to use a key held in device secure storage;
- core reflection features do not require a CBT Cards account;
- the audited app includes Firebase Analytics, Crashlytics, Performance, Cloud Messaging, and Firestore;
- Analytics and Crashlytics collection are controlled by the app's analytics-consent setting in the audited implementation;
- Firestore is used for a shared card-popularity counter based on a card identifier rather than diary text;
- exports, platform sharing, and the optional user-initiated Google Drive backup can move supported data outside local storage by explicit user action.

This baseline must be rechecked against the exact current mobile source/build before it is used to correct store-console answers.

## Public-store observations on 19 August 2026

### Apple App Store

Public listing: `https://apps.apple.com/us/app/cbt-cards-%D1%81bt-for-daily-use/id6737169041`

Observed public metadata:

- current public release label: **Version 3.0 CBT**;
- App Privacy lists **Identifiers** in the tracking category;
- App Privacy lists **Usage Data** as not linked to identity;
- marketing copy on the same listing uses broader tracking-free wording.

The public page therefore contains claims that cannot all be treated as one precise technical statement. App Store Connect answers and the shipped iOS implementation need to be checked together.

### Google Play

Public listing: `https://play.google.com/store/apps/details?id=cbt.cbtcards.stressrelief`

Observed public metadata:

- public page shown as updated **9 March 2026**;
- Data Safety says the app may share **App activity** and **App info and performance** with third parties;
- a separate Data Safety field indicates collection is absent;
- marketing copy uses broader tracking-free wording;
- the public listing does not expose enough build detail to identify the exact Android source revision used for the disclosure audit.

The Play Console answers and the current Android build therefore remain to be checked together.

## Important distinction

Store privacy categories about identifiers, usage data, app activity, diagnostics, or performance are not evidence that diary entries, check-ins, note text, or attached-photo contents are uploaded. Those private reflection contents and technical telemetry are separate data classes.

The reverse is also true: local handling of reflection content does not justify an absolute statement about all technical telemetry. Firebase/SDK behavior, identifiers, consent initialization, and store disclosure answers have to be verified independently.

## Required implementation verification

Before issue #3 can be closed, record all of the following for the current released builds:

1. iOS source commit/tag and App Store build/version corresponding to **Version 3.0 CBT**.
2. Android source commit/tag and the Play-distributed version/build.
3. Exact Firebase SDKs and initialization/configuration in each build.
4. Whether Analytics, Crashlytics, and Performance start before or after consent and what disabling consent changes in practice.
5. Whether Firebase Cloud Messaging identifiers/tokens are created or transmitted and under which conditions.
6. Firestore payloads for the shared-card counter and confirmation that reflection contents are excluded.
7. Any advertising, attribution, deep-link, analytics, or other third-party SDK not already represented in the July audit.
8. Any IDFA, ATT, Android advertising ID, app-instance identifier, installation identifier, or equivalent access/use.
9. Current App Store Connect privacy answers and the reasoning/source evidence for each answer.
10. Current Google Play Data Safety answers and the reasoning/source evidence for each answer.
11. The final store-answer update date and the app version/build against which the answers were verified.

## Publication rule while reconciliation is open

The website should make narrow, implementation-scoped statements. Public CBT Cards HTML must not use absolute tracking/data-collection slogans while Apple/Google disclosures remain unresolved. Store metadata should be described as an observation requiring verification, not silently copied into the website as implementation truth.

The canonical user-facing policy remains `https://cbt-cards.github.io/privacy/`.
