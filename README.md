# nongkrong

(*in development*)

Composition environment / library for an experimental, Gamelan-like music ensemble.
In the ensemble all metal instruments have been replaced by string instruments and two additional bamboo flutes.

## Purpose

*nongkrong* supports the composition process for the mentioned ensemble. It offers abstractions for its tonal and rhythmic potential, its instruments and their notation.

This README tries to give a rough overview about musical concepts and preconditions of the ensemble design. For more details it is recommended to check the specific subfolders and files in the project tree.

## Instruments

Instruments of the ensemble may finally include...

	* an adapted *gamelan siteran* - ensemble:
		* one siter panerus
		* one siter barung
		* two siter slenthem
		* one 'siter gong' 
	* different adapted Sundanese instruments:
		* two adapted kecapi siter
		* six Sundanese kendang anak
	* other:
		* two bamboo slide flutes
		* one Burmese bamboo clapper
		* one Javanese slit drum (Kenthongan)

Different plans and sketches as well as expected tunings for the individual instruments can be found [here](https://github.com/uummoo/nongkrong/blob/master/other/instruments).

(2019.03.05) Most of the instruments are still in production, produced by four different *Pengrajin Gamelan* in the cities of Yogyakarta, Surakarta and Bandung:

	* Hj. Mulyaningsih. TOKO POLOWIJAN. (Yogyakarta)
	* Bondho Gongso. TRI SUKO ASMORO HADI. (Yogyakarta)
	* Mas PM (Surakarta)
	* Sabilulungan (Bandung)


The ensemble is supposed to be played by 9 persons.

## Tuning

The tuning of the ensemble is based on a [hexany](http://anaphoria.com/hexany.pdf) (3-5-7-9) ([Wilsons combination-product-set scales](http://anaphoria.com/wilsoncps.html)). The instruments are therefore tuned in Just Intonation (as good as it's possible). While the scale is clearly represented by the siter slenthem, the pitches of other registers and instruments differ from the mentioned scale.

Due to the bipartite character of Just Intonation intervals in their mathematical representation, the tonal material is deeply dichotomous. This dichotomy is fairly represented by the *bolak-balik* - principle of the Javanese siter. Because of this, the siter players have to turn around their instrument if the mode is shifting from positive to negative or upside down. The kecapi players on the other hand just change their roles, meaning the player who played the slower part before, will turn over to the faster part and vice versa. The flutes as well as the kendang already contain all necessary pitches for both modes (positive and negative), meaning they don't have to change anything in case of a modulation.

## Notation

Instead of Western staff notation, the project uses an extended version of the Javanese *notasi kepatihan* (number notation). This decision is justified by the fact that most of people who will play instruments in this ensemble never played those instruments before or at least in a very different manner. Undoubtably no one ever played them with any Western notation.

While Western notation is more precise in rhythm, it is also more difficult to learn for a new instrument than the simple-to-read number notation. And since most of instruments only contain small ambitus, numbers are absolutely sufficient.

To avoid the complicated problem of microtonal notation, this project will just stick on tablatures. Therefore it's important to keep in mind that the individual numbers in this notation don't represent specific pitches like in its Javanese complement, but are rather indicating which string or drum the player has to hit at a specific time.

The biggest difference between the traditional *kepatihan* notation and its adaption in this project could be found in the fact that the Javanese original is firstly intented to be a memory aid while this adaption is supposed to be read while playing.

## About the project name

The Indonesian word *nongkrong* literally means 'to squat'. In its more daily context it refers to "hangout" or "to do nothing in particular", "to spend time together doing nothing". While walking through a central Javanese city during the night, plenty of people can be seen, sitting along the street, drinking tea and doing nothing special for hours. In this way *nongkrong* becomes a symbol for the Javanese time perception whose uniquity and difference to its Western counterpart is remarkable. This time perception is of course also recognizable in Javanese music. The most picturesque example may be found in the famous *Wayang Kulit* (shadow puppetry). Those shows can last 6-7 hours from the evening until the morning with the musicans eating, talking and finally falling asleep in between. In this way *nongkrong* indicates a specific musical concept of time, where time itself becomes absent. The music resulting from this project aims to follow this notion of time.

