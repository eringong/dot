//
//  ViewController.swift
//  dot_2
//
//  Created by Erin Gong on 11/11/14.
//  Copyright (c) 2014 Erin Gong. All rights reserved.
//

import UIKit
import CoreLocation
import Foundation

var urlString = NSString()
var result = NSString()
var det_lab : String = "waiting for beacon data"

class ViewController: UIViewController, UITableViewDelegate, UITableViewDataSource, UITextFieldDelegate {
    @IBOutlet var scan_table: UITableView!
    @IBOutlet var time_label:UILabel!
    @IBOutlet var location_pred_label:UILabel!
    
    var beacons: [CLBeacon]?
    var loc_pred: [String] = []

    override func viewDidLoad() {
        super.viewDidLoad()

        self.scan_table.registerClass(UITableViewCell.self, forCellReuseIdentifier: "cell2")
        location_pred_label.text = "\(result)"
        

    }
    
}

extension ViewController: UITableViewDataSource {

    func tableView(tableView: UITableView,
        numberOfRowsInSection section: Int) -> Int {
                if(beacons != nil) {
                    return beacons!.count
                } else {
                    return 0
                }
            }

    func tableView(tableView: UITableView,
        cellForRowAtIndexPath indexPath: NSIndexPath) -> UITableViewCell {
            var cell2:UITableViewCell? = self.scan_table.dequeueReusableCellWithIdentifier("cell2") as? UITableViewCell
            
            if(cell2 == nil) {
                cell2 = UITableViewCell(style: UITableViewCellStyle.Subtitle, reuseIdentifier: "cell2")
                cell2!.selectionStyle = UITableViewCellSelectionStyle.None
            }
            
            let beacon:CLBeacon = beacons![indexPath.row]

            det_lab = "RSSI: \(beacon.rssi as Int)," +
                "Maj: \(beacon.major.integerValue)," +
                "Min: \(beacon.minor.integerValue)"
            cell2!.textLabel!.text = det_lab
            
            return cell2!
        }

}

