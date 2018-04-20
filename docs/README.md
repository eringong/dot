# Dot

Tracking indoor location using iBeacons. Built as a hobby project for tracking visitor location in museums and galleries.

## Components

Dot includes

1) Two iOS apps for saving iBeacons RSSI data feeds to Firebase. The dot_labeler app is designed for a trained data collector to generate labeled datasets. It has a screen interface for labeling which gallery you are in within a museum. The dot_collector app is designed for a visitor to carry in the museum while it passively uploads sensor data to Firebase.

2) Real-time python script that ingests iBeacon RSSI data feeds, runs them through a classifier, and spits out real-time classification. This was designed to get real-time feedback on algorithm performance while moving through different locations in the museum. Helpful for diagnosing specific trouble zones in the physical space.

3) 2-stage classifier (k-nearest neighbors + hidden markov model) that classifies RSSI data feeds into sub-locations within a museum space.

4) (forthcoming) Data visualization of visitor pathways through the museum space.

## Notes

This is not a generalized library meant for broad application of iBeacon indoor positioning. It is an example of how indoor positioning can be used, particularly looking at the success of machine learning techniques on this data source. The code base is specific to the particular museum and set up it was originally deployed on.

The iOS apps were built in 2014 and are likely very outdated. They have not been recently tested. Probably not super valuable as code, but helps illustrate how data was collected.